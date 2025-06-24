from enum import Enum
from typing import Literal
class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def str_values(cls)  -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def get(cls, key):
        return member.value if (member := cls.__members__.get(key)) else None

LookerMeasureType = Literal[
    "number",
    "string",
    "average",
    "average_distinct",
    "count",
    "count_distinct",
    "list",
    "max",
    "median",
    "median_distinct",
    "min",
    "sum",
    "sum_distinct",
    "yesno",
    "percentage_of_previous",
    "percentage_of_total",
    "percentile",
    "percentile_distinct",
    "running_total",
]

LookerDataType = Literal[
    "epoch",
    "timestamp",
    "date",
    "datetime",
    "yyyymmdd",
]

LookerType = Literal[
        "bin",
        "date",
        "datetime",
        "distance",
        "duration",
        "location",
        "number",
        "string",
        "tier",
        "time",
        "yesno",
        "zipcode",
        "timestamp",
    ]

class LookerTimeMeasureType(str, ExtendedEnum):
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    COUNT_DISTINCT = "count_distinct"


class LookerValueFormatName(str, ExtendedEnum):
    DECIMAL_0 = "decimal_0"
    DECIMAL_1 = "decimal_1"
    DECIMAL_2 = "decimal_2"
    DECIMAL_3 = "decimal_3"
    DECIMAL_4 = "decimal_4"
    USD_0 = "usd_0"
    USD = "usd"
    GBP_0 = "gbp_0"
    GBP = "gbp"
    EUR_0 = "eur_0"
    EUR = "eur"
    ID = "id"
    PERCENT_0 = "percent_0"
    PERCENT_1 = "percent_1"
    PERCENT_2 = "percent_2"
    PERCENT_3 = "percent_3"
    PERCENT_4 = "percent_4"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class LookerTimeFrame(str, ExtendedEnum):
    DATE = "date"
    DAY_OF_MONTH = "day_of_month"
    DAY_OF_WEEK = "day_of_week"
    DAY_OF_WEEK_INDEX = "day_of_week_index"
    DAY_OF_YEAR = "day_of_year"
    FISCAL_MONTH_NUM = "fiscal_month_num"
    FISCAL_QUARTER = "fiscal_quarter"
    FISCAL_QUARTER_OF_YEAR = "fiscal_quarter_of_year"
    FISCAL_YEAR = "fiscal_year"
    HOUR = "hour"
    HOUR2 = "hour2"
    HOUR3 = "hour3"
    HOUR4 = "hour4"
    HOUR6 = "hour6"
    HOUR8 = "hour8"
    HOUR12 = "hour12"
    HOUR_OF_DAY = "hour_of_day"
    MICROSECOND = "microsecond"
    MILLISECOND = "millisecond"
    MILLISECOND2 = "millisecond2"
    MILLISECOND4 = "millisecond4"
    MILLISECOND5 = "millisecond5"
    MILLISECOND8 = "millisecond8"
    MILLISECOND10 = "millisecond10"
    MILLISECOND20 = "millisecond20"
    MILLISECOND25 = "millisecond25"
    MILLISECOND40 = "millisecond40"
    MILLISECOND50 = "millisecond50"
    MILLISECOND100 = "millisecond100"
    MILLISECOND125 = "millisecond125"
    MILLISECOND200 = "millisecond200"
    MILLISECOND250 = "millisecond250"
    MILLISECOND500 = "millisecond500"
    MINUTE = "minute"
    MINUTE2 = "minute2"
    MINUTE3 = "minute3"
    MINUTE4 = "minute4"
    MINUTE5 = "minute5"
    MINUTE6 = "minute6"
    MINUTE10 = "minute10"
    MINUTE12 = "minute12"
    MINUTE15 = "minute15"
    MINUTE20 = "minute20"
    MINUTE30 = "minute30"
    MONTH = "month"
    MONTH_NAME = "month_name"
    MONTH_NUM = "month_num"
    QUARTER = "quarter"
    QUARTER_OF_YEAR = "quarter_of_year"
    RAW = "raw"
    SECOND = "second"
    TIME = "time"
    TIME_OF_DAY = "time_of_day"
    WEEK = "week"
    WEEK_OF_YEAR = "week_of_year"
    YEAR = "year"
    YESNO = "yesno"


class LookerBigQueryDataType(str, ExtendedEnum):
    INT64 = "number"
    INTEGER = "number"
    FLOAT = "number"
    FLOAT64 = "number"
    NUMERIC = "number"
    BIGNUMERIC = "number"
    BOOLEAN = "yesno"
    STRING = "string"
    TIMESTAMP = "timestamp"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "string" 
    BOOL = "yesno"
    GEOGRAPHY = "string"
    BYTES = "string"
    ARRAY = "string"
    STRUCT = "string"
    JSON = "string"
    RECORD = "string"
    STR = "string"


class LookerDateTimeTypes(str, ExtendedEnum):
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"


class LookerDateTypes(str, ExtendedEnum):
    DATE = "date"


class LookerScalarTypes(str, ExtendedEnum):
    NUMBER = "number"
    YESNO = "yesno"
    STRING = "string"


class LookerDateTimeframes(str, ExtendedEnum):
    RAW = "raw"
    DATE = "date"
    DAY_OF_MONTH = "day_of_month"
    DAY_OF_WEEK = "day_of_week"
    DAY_OF_WEEK_INDEX = "day_of_week_index"
    WEEK = "week"
    WEEK_OF_YEAR = "week_of_year"
    MONTH = "month"
    MONTH_NUM = "month_num"
    MONTH_NAME = "month_name"
    QUARTER = "quarter"
    QUARTER_OF_YEAR = "quarter_of_year"
    YEAR = "year"


class LookerTimeTimeframes(str, ExtendedEnum):
    RAW = "raw"
    TIME = "time"
    TIME_OF_DAY = "time_of_day"
    DATE = "date"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class LookerRelationshipType(str, ExtendedEnum):
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"


class LookerJoinType(str, ExtendedEnum):
    LEFT_OUTER = "left_outer"
    FULL_OUTER = "full_outer"
    INNER = "inner"
    CROSS = "cross"