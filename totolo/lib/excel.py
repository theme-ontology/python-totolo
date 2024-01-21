import re


def xls_sheet_to_memory(filename, sheets='ALL'):
    import pandas as pd
    outdict = {}
    pdict = pd.read_excel(
        filename, sheet_name=None, header=None, dtype=str, na_filter=False
    )
    if sheets == 'ALL':
        sheet_names = set(pdict)
    else:
        sheet_names = set([sheets]) if isinstance(sheets, str) else set(sheets)
    for sheetname in pdict:
        if sheetname in sheet_names:
            keystr = str(sheetname)
            allrows = pdict[sheetname].values.tolist()
            outdict[keystr] = allrows
    return outdict


def get_headers(filename, sheetpattern=".*"):
    results = []
    for sheetname, sheet in xls_sheet_to_memory(filename).items():
        if re.match(sheetpattern, sheetname):
            if sheet:
                results.append((sheetname, sheet[0]))
            else:
                results.append((sheetname, []))
    return results


def read_xls(filename, headers=None, sheetpattern=".*"):
    sheetcount = 0
    rowcount = 0
    results = []
    idxs = []
    sheets = xls_sheet_to_memory(filename)

    for sheetname, sheet in sheets.items():
        if not re.match(sheetpattern, sheetname):
            continue
        sheetcount += 1
        for idx, row in enumerate(sheet):
            if idx == 0:
                if headers is None:
                    headers = row
                    rowcount += 1
                    results.append(row)
                idxs = []
                for header in headers:
                    idxs.append(row.index(header))
            else:
                rowcount += 1
                results.append([row[i] for i in idxs])

    return results, sheetcount, rowcount
