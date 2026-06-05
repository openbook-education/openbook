# OpenBook: Interactive Online Textbooks
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import calendar

from datetime                   import datetime, timedelta

from django.contrib             import admin
from django.core.exceptions     import ValidationError
from django.db                  import models
from django.utils.translation   import gettext_lazy as _

class ValidityTimeSpanMixin(models.Model):
    """
    Mixin class for models that have a validity optionally starting at a certain point
    in time and optionally ending at a later point in time.
    """
    start_date = models.DateTimeField(verbose_name=_("Start date and time"), blank=True, null=True)
    end_date   = models.DateTimeField(verbose_name=_("End date and time"), blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self):
        """
        Custom check when the model is saved that the end date must be later then the
        start date, if both respective flags are set. If one of the two flags is unset
        the check will be skipped.

        Care must be taken to call this method, if the `clean()` method is overwritten by another
        mixin class or the model itself.
        """
        if self.start_date is not None and self.end_date is not None and self.start_date >= self.end_date:
            raise ValidationError(_("End date must be later than start date."))

    @property
    @admin.display(description=_("Limited Validity"))
    def validity_time_span(self):
        """
        Get formatted string to display in the Admin or on the website.
        """
        time_span = []

        if self.start_date is not None:
            time_span.append(_("Start: {start_date}").format(start_date=self.start_date.strftime("%x %X")))

        if self.end_date is not None:
            time_span.append(_("End: {end_date}").format(end_date=self.end_date.strftime("%x %X")))

        return " - ".join(time_span) if time_span else ""

class DurationMixin(models.Model):
    """
    Mixin class for models that have a duration in minutes, hours, days, weeks, months or years.
    """
    class DurationPeriod(models.TextChoices):
        MINUTES = "minutes", _("Minutes")
        HOURS   = "hours",   _("Hours")
        DAYS    = "days",    _("Days")
        WEEKS   = "weeks",   _("Weeks")
        MONTHS  = "months",  _("Months")
        YEARS   = "years",   _("Years")

    duration_period = models.CharField(verbose_name=_("Duration Period"), max_length=10, choices=DurationPeriod, null=False, blank=True)
    duration_value = models.FloatField(verbose_name=_("Duration Value"), null=False, blank=True)

    class Meta:
        abstract = True
    
    @property
    @admin.display(description=_("Duration"))
    def duration(self):
        """
        Get formatted string to display in the Admin or on the website.
        """
        if self.duration_value and self.duration_period:
            try:
                return f"{self.duration_value} {self.DurationPeriod(self.duration_period).label}"
            except ValueError:
                return f"{self.duration_value} {self.duration_period}"
        else:
            return ""

    def save(self, *args, **kwargs):
        """
        Make sure to not fail the NOT NULL constraint on duration value.
        """
        if not self.duration_value:
            self.duration_value = 0.0
        
        super().save(*args, **kwargs)

    def add_duration_to(self, timestamp: datetime) -> datetime:
        """
        Add the specified duration to the given timestamp.
        """
        match self.duration_period:
            case self.DurationPeriod.MINUTES:
                return timestamp + timedelta(minutes=self.duration_value)
            
            case self.DurationPeriod.HOURS:
                return timestamp + timedelta(hours=self.duration_value)
            
            case self.DurationPeriod.DAYS:
                return timestamp + timedelta(days=self.duration_value)
            
            case self.DurationPeriod.WEEKS:
                return timestamp + timedelta(weeks=self.duration_value)
            
            case self.DurationPeriod.MONTHS:
                total_months   = timestamp.month + int(self.duration_value)
                year_increment = (total_months - 1) // 12
                new_month      = (total_months - 1) % 12 + 1
                new_year       = timestamp.year + year_increment

                last_day       = calendar.monthrange(new_year, new_month)[1]
                new_day        = min(timestamp.day, last_day)

                return timestamp.replace(year=new_year, month=new_month, day=new_day)

            case self.DurationPeriod.YEARS:
                new_year = timestamp.year + int(self.duration_value)

                if timestamp.month == 2 and timestamp.day == 29:
                    # Not a leap year? Adjust to Feb 28
                    if not calendar.isleap(new_year):
                        return timestamp.replace(year=new_year, day=28)
                
                return timestamp.replace(year=new_year)

            case _:
                return timestamp