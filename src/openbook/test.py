# OpenBook: Interactive Online Textbooks - Server
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import copy
import functools
import json
import typing

from collections.abc                           import Iterable
from django.contrib.auth                       import get_user_model
from django.contrib.auth.models                import AbstractUser
from django.db.models.manager                  import Manager
from django.db.models                          import Model
from django.db.models                          import Manager
from django.db.models                          import QuerySet
from django.urls                               import reverse
from rest_framework.response                   import Response
from rest_framework.test                       import APIClient

from openbook.auth.middleware.current_user     import reset_current_user
from openbook.auth.models.anonymous_permission import AnonymousPermission
from openbook.auth.utils                       import permission_for_perm_string

User = get_user_model()

class _HttpMethod:
    """
    Utility class to call the right method on the API client depending on the HTTP method
    used by a REST operation.
    """
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name.upper()

    def call(self,
        client:       APIClient,
        path:         str,
        query_params: dict|None     = None,
        data:         dict|str|None = None,
        format:       str|None      = None,
        content_type: str|None      = None,
        **extra:      dict,
    ) -> Response:
        match self.name.lower():
            case "get":
                client_method = client.get
            case "put":
                client_method = client.put
            case "post":
                client_method = client.post
            case "patch":
                client_method = client.patch
            case "delete":
                client_method = client.delete
            case _:
                raise ValueError(f"Unsupported HTTP method: {self.name}")
        
        return client_method(path, data, query_params=query_params, format=format, content_type=content_type, **extra)
        
class ModelViewSetTestMixin:
    """
    Shared unit tests for the ModelViewSet based REST APIs. Defines parametrized unit tests for
    common behavior like searching, sorting and the usual REST HTTP methods. Use it like this:

    ```python
    class MyModel_ViewSet_Test(ModelViewSetTestMixin, TestCase):
        base_name         = "my_model"
        model             = MyModel
        pk_found          = 4711,
        search_string     = "test"
        search_count      = 2
        sort_field        = "fieldname"
        expandable_fields = ("fk_relation", "m2m_relation[]")

        def get_create_data(self):
            return {...}

        operations = {
            "create": {
                "request_data": get_create_data,    # Dict or method that returns dict
            },
            "update": {
                "request_data": {"some_field": "new value"},
                "updates": {"some_obj": {"id": "new_value"}},
            },
            "partial_update": {
                "request_data": {...},
                "updates": {...},
            },

            # Not supported operation
            "delete": {
                "supported": False,
            },

            # Custom action (without authentication/authorization)
            "custom": {
                "supported":          True,
                "http_method":        ModelViewSetTestMixin.HttpMethod.GET,
                "status_code":        200,      # Okay
                "url_suffix":         "custom",
                "requires_auth":      False,
                "model_permission":   (),
                "assertions":         (assertHealthStatus,),
            },
        }
    ```

    See the source of this class for all supported properties. There are lots more to cover
    special cases like custom permissions, non-authenticated operations and so on.

    Use a custom assertion method to check the object after updates, if the check based on the
    `"updates"` dict is too simple.

    This mixin creates lots of additional test methods via meta-programming to assert that
    for each endpoint (operation) the REST API uses authentication, authorization, returns
    the expected status code and performs the expected actions. Additional test methods may
    be manually created as usual, to test special behavior beyond this.
    """
    #---------------#
    # Configuration #
    #---------------#

    class HttpMethod:
        GET    = _HttpMethod("get")
        PUT    = _HttpMethod("put")
        POST   = _HttpMethod("post")
        PATCH  = _HttpMethod("patch")
        DELETE = _HttpMethod("delete")

    base_name = "change_me"
    """Base name as defined in the DRF router"""

    model: Model = None
    """Model class for automatically determining required permissions"""

    count: int = 0
    """Expected list count, if not just all model entries. Set to < 0 to disable, or > 0 to override database lookup."""

    pk_field = "pk"
    """Name of the key field of the model (for testing that DELETE actually deletes the object)"""

    pk_found = "change-me"
    """String or method to get key value of an existing object for testing the detail operations"""

    pk_not_found = "not-found"
    """String or method to get key value of a non-existing object for testing the 404 status code"""

    search_string = "",
    """Search string to test the `_search` query parameter (will not be tested if string is empty)"""

    search_count = -1
    """Number of expected search results when testing the `_search` query parameter"""

    sort_field = ""
    """Fieldname to test the `_sort` query parameter (will not be tested if string is empty)"""

    expandable_fields = ()
    """List of expandable relation fields to test that expansion doesn't crash. Fields ending with `[]` are tested as lists."""

    operations = {
        "list": {
            "supported":          True,                     # Operation is supported by the webservice
            "http_method":        HttpMethod.GET,           # HTTP method to call this endpoint
            "status_code":        200,      # Okay          # Expected status code on success
            "url_suffix":         "list",                   # Suffix for reverse(f"{base_name}-{suffix}")
            "url_has_pk":         False,                    # Whether the PK must be appended to the URL
            "requires_auth":      True,                     # Whether the operation requires a logged-in user
            "username":           "",                       # Existing user to login with, otherwise a new one will be created
            "password":           "",                       # Password for existing user
            "model_permission":   ("view",),                # Model permissions the user must have (as in "app.view_model")
            "custom_permissions": [],                       # Additional custom permission strings to check
            "request_data":       None,                     # Dict or method that returns dict to get request body data (to create or update an object)
            "format":             None,                     # APIClient parameter format
            "content_type":       "",                       # APIClient parameter content_type: 
            "extra":              {},                       # APIClient parameter extra
            "updates":            {},                       # Dict or method that returns dict with expected values after an update
            "assertions":         (),                       # Callback functions that receive the response object to check extra assertions
        },
        "create": {
            "supported":          True,
            "http_method":        HttpMethod.POST,
            "status_code":        201,      # Created
            "url_suffix":         "list",
            "url_has_pk":         False,
            "requires_auth":      True,
            "username":           "",
            "password":           "",
            "model_permission":   ("view", "add",),
            "custom_permissions": [],
            "request_data":       None,
            "format":             None,
            "content_type":       "",
            "extra":              {},
            "updates":            {},
            "assertions":         (),
        },
        "retrieve": {
            "supported":          True,
            "http_method":        HttpMethod.GET,
            "status_code":        200,      # Okay
            "url_suffix":         "detail",
            "url_has_pk":         True,
            "requires_auth":      True,
            "username":           "",
            "password":           "",
            "model_permission":   ("view",),
            "custom_permissions": [],
            "request_data":       None,
            "format":             None,
            "content_type":       "",
            "extra":              {},
            "updates":            {},
            "assertions":         (),
        },
        "update": {
            "supported":          True,
            "http_method":        HttpMethod.PUT,
            "status_code":        200,      # Okay
            "url_suffix":         "detail",
            "url_has_pk":         True,
            "requires_auth":      True,
            "username":           "",
            "password":           "",
            "model_permission":   ("view", "change"),
            "custom_permissions": [],
            "request_data":       None,
            "format":             None,
            "content_type":       "",
            "extra":              {},
            "updates":            {"change_me": True},
            "assertions":         (),
        },
        "partial_update": {
            "supported":          True,
            "http_method":        HttpMethod.PATCH,
            "status_code":        200,      # Okay
            "url_suffix":         "detail",
            "url_has_pk":         True,
            "requires_auth":      True,
            "username":           "",
            "password":           "",
            "model_permission":   ("view", "change"),
            "custom_permissions": [],
            "request_data":       None,
            "format":             None,
            "content_type":       "",
            "extra":              {},
            "updates":            {"change_me": True},
            "assertions":         (),
        },
        "destroy": {
            "supported":          True,
            "http_method":        HttpMethod.DELETE,
            "status_code":        204,      # No Content
            "url_suffix":         "detail",
            "url_has_pk":         True,
            "requires_auth":      True,
            "username":           "",
            "password":           "",
            "model_permission":   ("view", "delete"),
            "custom_permissions": [],
            "request_data":       None,
            "format":             None,
            "content_type":       "",
            "extra":              {},
            "updates":            {},
            "assertions":         (),
        },
    }
    """
    Test configuration for each supported operation. Contains all the standard operations like
    "list", "change", etc. but you can also add additional entries for custom actions defined
    with the `@action` decorator in the view set. In that case use the constants defined in the
    inner class `HttpMethod` to set the HTTP method for the new operation. The expected status
    codes will be automatically determined as per the other values.

    When adding custom actions, make sure to set the `"url_suffix"` to the action name and to
    set `"url_has_pk"` to `True`, when it is an action for a single object.

    For unsupported operations the key `"supported"` should be set to `False`. This lets the test
    case test that it is really unsupported.
    
    Note, that test users will be automatically created to test the permissions. The permissions
    will be directly assigned to the users as user permissions. Scoped permissions need to be
    checked separately, but usually it is not necessary to test scoped permissions for each view
    set. It is sufficient to test that scoped permissions work in general.
    """

    @classmethod
    def __init_subclass__(cls):
        """
        Merge configured operations from the subclass with the template defined in this class.
        In the subclass only the values to be changed need to be declared. All other values
        are copied from the base class.
        """
        super().__init_subclass__()

        # Merge configuration for the REST operations
        operations_merged   = copy.deepcopy(ModelViewSetTestMixin.operations)
        operations_subclass = getattr(cls, "operations", {})

        for operation, overrides in operations_subclass.items():
            if operation in operations_merged:
                # Patched configuration for existing operation
                if overrides:
                    # Partially override attributes of an existing operation
                    operations_merged[operation].update(overrides)
                else:
                    # Remove (disable) the whole operation
                    operations_merged[operation] = overrides
        
        for operation, overrides in operations_subclass.items():
            if not operation in operations_merged:
                # New operation defined in subclass
                if not "list" in operations_merged:
                    raise KeyError(f"Cannot test custom action {operation}. Custom operations require the list operation as a template.")

                operations_merged[operation] = copy.deepcopy(operations_merged["list"])
                operations_merged[operation].update(overrides)

        cls.operations = operations_merged

        # Dynamically create test methods
        if cls.count != 0:
            expected_count = cls.count
        else:
            expected_count = cls.model.objects

        assertions_empty_list = (functools.partial(cls.assertResultList, expected_count=0),)
        assertions_one_item   = (functools.partial(cls.assertResultList, expected_count=1),)
        assertions_full_list  = (functools.partial(cls.assertResultList, expected_count=expected_count),)
        assertions_search     = (functools.partial(cls.assertResultList, expected_count=cls.search_count),)
        assertions_sort       = (functools.partial(cls.assertSortOrder, sort_field=cls.sort_field),)
        assertions_create     = (functools.partial(cls.assertObjectCreated, pk_field=cls.pk_field, pk_found=cls.pk_found),)
        assertions_destroy    = (functools.partial(cls.assertObjectDeleted, pk_field=cls.pk_field, pk_found=cls.pk_found),)
        assertions_expanded   = (functools.partial(cls.assertFieldsExpanded, expandable_fields=cls.expandable_fields),)

        if cls.model and issubclass(cls.model, AbstractUser):
            # Special case: Unit testing a model viewset for the User model.
            # In this case even without permissions the temporary test user
            # will be returned for the list operation.
            assertions_empty_list = assertions_one_item

        for operation, configuration in operations_merged.items():
            # For tests with missing authentication we cannot use a pre-defined user that
            # might actually have the required permissions.
            configuration_no_user = copy.deepcopy(configuration)
            configuration_no_user["username"] = ""
            configuration_no_user["password"] = ""

            # Operation not supported
            if not configuration["supported"]:
                setattr(cls, f"test_{operation}_not_supported", cls._create_test_method(
                    configuration   = configuration,
                    create_user     = True,
                    add_permissions = True,
                    pk_value        = cls.pk_found,
                    query_params    = {"_sort": cls.sort_field},
                    status_code     = 405,          # Method Not Allowed
                ))

                continue

            # Operation supported
            assertions_operation = [*configuration["assertions"]]

            if operation == "list":
                assertions_operation.extend(assertions_full_list)
            elif operation == "create":
                assertions_operation.extend(assertions_create)
            elif operation == "destroy":
                assertions_operation.extend(assertions_destroy)
            elif operation in ["update", "partial_update"]:
                assertions_operation.append(
                    functools.partial(cls.assertObjectUpdated,
                        pk_field = cls.pk_field,
                        pk_found = cls.pk_found,
                        updates  = configuration["updates"]
                    )
                )

            if not configuration["requires_auth"]:
                # Unauthenticated usage is allowed, but still anonymous permissions must be set
                if configuration["model_permission"] or configuration["custom_permissions"]:
                    if operation == "list":
                        setattr(cls, f"test_{operation}_anonymous_unauthorized", cls._create_test_method(
                            configuration   = configuration_no_user,
                            create_user     = False,
                            add_permissions = False,
                            pk_value        = cls.pk_found,
                            query_params    = {"_sort": cls.sort_field},
                            status_code     = 200,          # Empty list expected if no permission
                            assertions      = assertions_empty_list
                        ))
                    else:
                        setattr(cls, f"test_{operation}_anonymous_unauthorized", cls._create_test_method(
                            configuration   = configuration_no_user,
                            create_user     = False,
                            add_permissions = False,
                            pk_value        = cls.pk_found,
                            query_params    = {"_sort": cls.sort_field},
                            status_code     = [403, 404],   # Forbidden (permission missing) or Not Found (hidden by permission)
                        ))

                setattr(cls, f"test_{operation}_anonymous_authorized", cls._create_test_method(
                    configuration   = configuration,
                    create_user     = False,
                    add_permissions = True,
                    pk_value        = cls.pk_found,
                    status_code     = configuration["status_code"],
                    query_params    = {"_sort": cls.sort_field},
                    assertions      = assertions_operation,
                ))
            else:
                # User must be logged-in and authorized
                setattr(cls, f"test_{operation}_unauthenticated", cls._create_test_method(
                    configuration   = configuration_no_user,
                    create_user     = False,
                    add_permissions = False,
                    pk_value        = cls.pk_found,
                    query_params    = {"_sort": cls.sort_field},
                    status_code     = [401, 403],          # Unauthorized (login required) or Forbidden (permission missing)
                ))

            if configuration["model_permission"] or configuration["custom_permissions"]:
                if operation == "list":
                    setattr(cls, f"test_{operation}_unauthorized", cls._create_test_method(
                        configuration   = configuration_no_user,
                        create_user     = True,
                        add_permissions = False,
                        pk_value        = cls.pk_found,
                        query_params    = {"_sort": cls.sort_field},
                        status_code     = 200,          # Empty list expected if no permission
                        assertions      = assertions_empty_list
                    ))
                else:
                    setattr(cls, f"test_{operation}_unauthorized", cls._create_test_method(
                        configuration   = configuration_no_user,
                        create_user     = True,
                        add_permissions = False,
                        pk_value        = cls.pk_found,
                        query_params    = {"_sort": cls.sort_field},
                        status_code     = [403, 404],   # Forbidden (permission missing) or Not Found (hidden by permission)
                    ))

            setattr(cls, f"test_{operation}_authorized", cls._create_test_method(
                configuration   = configuration,
                create_user     = True,
                add_permissions = True,
                pk_value        = cls.pk_found,
                status_code     = configuration["status_code"],
                query_params    = {"_sort": cls.sort_field},
                assertions      = assertions_operation,
            ))

            if operation == "list":
                if cls.search_string:
                    setattr(cls, f"test_{operation}_search", cls._create_test_method(
                        configuration   = configuration,
                        create_user     = True,
                        add_permissions = True,
                        status_code     = configuration["status_code"],
                        query_params    = {"_search": cls.search_string, "_sort": cls.sort_field},
                        assertions      = assertions_search,
                    ))

                if cls.sort_field:
                    setattr(cls, f"test_{operation}_sort", cls._create_test_method(
                        configuration   = configuration,
                        create_user     = True,
                        add_permissions = True,
                        status_code     = configuration["status_code"],
                        query_params    = {"_sort": cls.sort_field},
                        assertions      = assertions_sort,
                    ))

                    setattr(cls, f"test_{operation}_pagination", cls._create_test_method(
                        configuration   = configuration,
                        create_user     = True,
                        add_permissions = True,
                        status_code     = configuration["status_code"],
                        query_params    = {"_page_size": "1", "_page": "1", "_sort": cls.sort_field},
                        assertions      = assertions_one_item,
                    ))
            elif operation == "retrieve":
                setattr(cls, f"test_{operation}_not_found", cls._create_test_method(
                    configuration   = configuration,
                    create_user     = True,
                    add_permissions = True,
                    pk_value        = cls.pk_not_found,
                    status_code     = 404,      # Not Found
                ))

                if cls.expandable_fields:
                    query_expand = ""

                    for fieldname in cls.expandable_fields:
                        fieldname    = fieldname[:-2] if fieldname.endswith("[]") else fieldname
                        query_expand = f"{query_expand},{fieldname}" if query_expand else fieldname

                    setattr(cls, f"test_{operation}_expand_fields", cls._create_test_method(
                        configuration   = configuration,
                        create_user     = True,
                        add_permissions = True,
                        pk_value        = cls.pk_found,
                        status_code     = 200,      # Okay
                        query_params    = {"_expand": query_expand},
                        assertions      = assertions_expanded,
                    ))

    @classmethod
    def _create_test_method(cls,
        configuration:   dict = {},
        create_user:     bool = False,
        add_permissions: bool = False,
        status_code:     int|typing.Iterable[int] = [],
        pk_value:        str|None = "",
        query_params:    dict = {},
        assertions:      typing.Iterable[typing.Callable[[Response], None]] = [],
    ):
        """
        Factory for the dynamically created test methods.
        """
        def test(self):
            # Create user with necessary permissions and login
            if add_permissions:
                perm_strings = [*configuration["custom_permissions"]]

                for action in configuration["model_permission"]:
                    app_label  = self.model._meta.app_label
                    model_name = self.model._meta.model_name
                    perm_strings.append(f"{app_label}.{action}_{model_name}")
            else:
                perm_strings = []

            if create_user:
                if configuration["username"]:
                    self.login(username=configuration["username"], password=configuration["password"])

                    user = User.objects.get(username=configuration["username"])

                    for perm_string in perm_strings:
                        user.user_permissions.add(permission_for_perm_string(perm_string))
                else:
                    self.create_user_and_login(perm_strings)
            else:
                self.logout()

                for perm_string in perm_strings:
                    AnonymousPermission.objects.create(permission=permission_for_perm_string(perm_string))

            # Call REST endpoint
            if pk_value and configuration["url_has_pk"]:
                args = (pk_value(self) if callable(pk_value) else pk_value,)
            else:
                args = None

            path = reverse(f"{cls.base_name}-{configuration["url_suffix"]}", args=args)
            request_data = configuration["request_data"]

            if callable(request_data):
                request_data = request_data(self)

            response = configuration["http_method"].call(
                client       = self.client,
                path         = path,
                query_params = query_params,
                data         = request_data,
                format       = configuration["format"],
                content_type = configuration["content_type"],
                extra        = configuration["extra"],
            )

            # Check HTTP response
            try:
                self.assertStatusCode(response, status_code)
                
                for assertion in assertions:
                    assertion(self, response)
            except:
                print()
                print(f"Request: {configuration["http_method"]} {path} {query_params}")
                print()

                if request_data:
                    try:
                        print(json.dumps(request_data, indent=4))
                        print()
                    except TypeError:
                        print(request_data)
                
                print(f"Response: {response.status_code}")

                try:
                    print(json.dumps(response.data, indent=4))
                except TypeError:
                    print(response.data)
                    
                raise

        return test

    # ----------------#
    # Utility methods #
    # ----------------#

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        reset_current_user()
    
    def login(self, username: str = None, password: str = None):
        """
        (Re)login with another user.
        """
        reset_current_user()
        self.client.logout()
        self.client.login(username=username, password=password)
    
    def create_user_and_login(self, perm_strings: typing.Iterable[str]) -> AbstractUser:
        """
        Create new user with the given permissions and login.
        """
        user = User.objects.create_user("rest-test-user", password="password", email="rest-test-user@test.com")
        self.login("rest-test-user", password="password")

        permissions = [permission_for_perm_string(perm_string) for perm_string in perm_strings]
        user.user_permissions.set(permissions)

        return user

    def logout(self):
        """
        Logout.
        """
        reset_current_user()
        self.client.logout()

    def assertStatusCode(self, response, expected_status_code: int|typing.Iterable[int]):
        """
        Assert status code in HTTP response.
        """
        if isinstance(expected_status_code, typing.Iterable):
            self.assertIn(response.status_code, expected_status_code, f"Expected HTTP status code in {expected_status_code} but got {response.status_code}")
        else:
            self.assertEqual(response.status_code, expected_status_code, f"Expected HTTP status code {expected_status_code} but got {response.status_code}")
    
    def assertResultList(self, response: Response, expected_count: int|QuerySet|Manager|typing.Iterable):
        """
        Assert response data contains a result list with the expected number of entries.
        The result count will only be checked if `expected_count` is at least zero.
        """
        if isinstance(expected_count, typing.Iterable):
            expected_count = len(list(expected_count))
        elif hasattr(expected_count, "count"):
            expected_count = expected_count.count()

        if isinstance(response.data, list):
            # Special case (e.g. scope type): Result is an array
            if expected_count >= 0:
                self.assertEqual(len(response.data), expected_count, f"Expected {expected_count} results but got {len(response.data)}")
        else:
            # Normale case: Result is an objects with `results` and `count`
            self.assertIn("results", response.data)
            self.assertIn("count", response.data)
            self.assertIsInstance(response.data["results"], list)

            if expected_count >= 0:
                # Beware of paging for large result sets!
                real_count = response.data["count"]

                if len(response.data["results"]) == expected_count:
                    real_count = len(response.data["results"])

                self.assertEqual(real_count, expected_count, f"Expected {expected_count} results but got {real_count}")
    
    def assertSortOrder(self, response: Response, sort_field: str):
        """
        Assert that the result list is sorted as expected.
        """
        self.assertIn("results", response.data)
        self.assertIsInstance(response.data["results"], list)

        sort_fields = sort_field.split("__")

        def sort_key(obj):
            for field in sort_fields:
                obj = obj[field]
            
            return obj

        results = response.data["results"]
        sorted_results = sorted(results, key=sort_key)
        self.assertEqual(results, sorted_results, f"Results are not sorted by {sort_field}")

    def assertFieldsExpanded(self, response: Response, expandable_fields: Iterable[str]):
        """
        Assert that the given fields have been expanded to objects or lists with objects.
        """
        for fieldname in expandable_fields:
            if fieldname.endswith("[]"):
                fieldname = fieldname[:-2]
                many = True
            else:
                many = False

            expanded_field = response.data[fieldname]

            if many:
                self.assertTrue(len(expanded_field) > 0, f"Expanded list {fieldname} has no entries")

                for child in expanded_field:
                    self.assertIsInstance(child, (dict, type(None)), f"Value {child} in expanded list {fieldname} is not an object")
            else:
                self.assertIsInstance(expanded_field, (dict, type(None)), f"Value {expanded_field} of expanded field {fieldname} is not an object")

    def assertObjectCreated(self, response: Response, pk_field: str, pk_found: str):
        """
        Assert that the object with the given key has been created.
        """
        if callable(pk_found):
            pk_found = pk_found(self)

        self.assertTrue(self.model.objects.filter(**{pk_field: pk_found}).exists())

    def assertObjectDeleted(self, response: Response, pk_field: str, pk_found: str):
        """
        Assert that the object with the given key has been deleted.
        """
        if callable(pk_found):
            pk_found = pk_found(self)

        self.assertFalse(self.model.objects.filter(**{pk_field: pk_found}).exists())
    
    def assertObjectUpdated(self, response: Response, pk_field: str, pk_found: str, updates: dict):
        """
        Assert that updates were fully applied.
        """
        if callable(pk_found):
            pk_found = pk_found(self)
        
        if callable(updates):
            updates = updates(self)

        def assert_updates(obj, upd: dict, full_key: str):
            for key, value in upd.items():
                new_full_key = f"{full_key}.{key}" if full_key else key

                if hasattr(obj, "get"):
                    new_value = obj.get(key)
                else:
                    new_value = getattr(obj, key)

                if isinstance(new_value, Manager):
                    new_value = new_value.all()

                if isinstance(value, dict):
                    assert_updates(new_value, value, new_full_key)
                elif isinstance(value, Iterable) and not isinstance(value, str):
                    for child_value in value:
                        found = False

                        for new_child_value in new_value:
                            try:
                                assert_updates(new_child_value, child_value, new_full_key)
                                found = True
                            except AssertionError:
                                pass

                        self.assertTrue(found, f"No child value was updated for key {new_full_key}")
                else:
                    self.assertEqual(new_value, value, f"Update expected for key {new_full_key}")

        obj = self.model.objects.get(**{pk_field: pk_found})
        assert_updates(obj, updates, "")
