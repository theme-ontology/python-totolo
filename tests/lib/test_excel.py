from contextlib import redirect_stderr, redirect_stdout
import totolo.lib.excel


XLS_PATH = "tests/data/scifi1920-mergelist.xlsx"


def test_xls_sheet_to_memory():
    result = totolo.lib.excel.xls_sheet_to_memory(XLS_PATH)
    assert len(result) > 1
    result = totolo.lib.excel.xls_sheet_to_memory(XLS_PATH, sheets='data')
    assert len(result) == 1
    result = totolo.lib.excel.xls_sheet_to_memory(XLS_PATH, sheets=['data'])
    assert len(result) == 1


def test_get_headers():
    result = dict(totolo.lib.excel.get_headers(XLS_PATH))
    assert result['empty'] == []


def test_read_xls():
    results, sheetcount, rowcount = totolo.lib.excel.read_xls(XLS_PATH, sheetpattern='data')
    assert sheetcount == 1
    assert rowcount >= 3
