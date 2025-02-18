from whenever import LocalDateTime, ZonedDateTime

d1 = LocalDateTime(2023, 10, 28, hour=22)
d2 = d1.assume_tz('US/Central', disambiguate='raise')
print(type(d1), d1)
print(type(d2), d2)


def test_incompatible_dts(d1: LocalDateTime, d2: ZonedDateTime):
    print(d1 + d2)
