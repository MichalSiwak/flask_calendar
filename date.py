import calendar
import datetime

days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']
months = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec',
          'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']

short_day_names = ['Pon', 'Wt ', 'Śr ', 'Cz ', 'Pt ', 'Sob', 'Ndz']


month_days = calendar.mdays
today_day_name = datetime.datetime.now()
today_date = datetime.date.today()
tomorrow_day_name = datetime.datetime.now() + datetime.timedelta(days=1)
tomorrow_date = (datetime.date.today() + datetime.timedelta(days=1))


def day(year, month, day):
    try:
        day_name = calendar.weekday(year, month, day)
        return [day, months[month], year, days[day_name]]
    except Exception:
        return False


def one_month(month, year):
    try:
        month = abs(int(month))
        year = abs(int(year))
        week_day_name = calendar.day_abbr
        calendar_months = calendar.monthcalendar(year, month)
        len_calendar_months = len(list(calendar_months))
        month_name = months[month]

        return [calendar_months, len_calendar_months, year, month_name, week_day_name]
    except Exception:
        return False


def one_year(year):
    try:
        months_name_list = list(calendar.month_name)
        week_day_name = calendar.day_abbr
        months = list(range(1, 13))
        year_calendar = []
        for month in months:
            month_day = calendar.monthcalendar(year, month)
            year_calendar.append(month_day)
        len_calendar_months = []
        for month in year_calendar:
            len_calendar_months.append(len(month))
        return [year_calendar, len_calendar_months, year, months_name_list, week_day_name]
    except Exception:
        return False
