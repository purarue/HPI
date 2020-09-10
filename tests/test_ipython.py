def test_ipython():
    from my.ipython import _parse_database

    # use the live database in XDG_DATA_HOME
    db = list(_parse_database())
    assert len(db) > 1
    item = db[0]
    assert bool(item.command.strip())