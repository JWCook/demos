from datetime import UTC, datetime, timezone

# current datetime in UTC
print(datetime.utcnow())
print(datetime.now(UTC))
print(datetime.now(timezone.utc))


def test_incompatible_dts_stdlib():
    print(datetime.now() + datetime.now(UTC))
