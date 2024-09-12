import argparse
import re

import pandas as pd

import totolo


REVIEW_COLS = [
    "sid",
    "title",
    "parents",
    "theme",
    "capacity",
    "weight",
    "motivation",
    "ACTION",
    "revised motivation",
    "revised theme",
    "revised weight",
    "revised capacity",
    "tentative action",
    "discussion thread",
]

REVIEW_COL_WIDTHS = {
    "weight": 10,
    "motivation": 40,
    "revised comment": 40,
    "revised weight": 10,
    "revised capacity": 10,
}

BASIC_CELL_STYLE = {
    'text_wrap': True,
    'valign': 'vcenter',
    'align': 'left',
    'border': 1,
    'border_color': '#cccccc',
}


def conditional_add_from(iterable, names, regex, container):
    for obj in iterable:
        if regex:
            if any(re.match(patt, obj.name) for patt in names):
                container.add(obj.name)
        elif obj.name in names:
            container.add(obj.name)


def write_themelist(df, filename, columns=None):
    df = df.copy()
    columns = columns or REVIEW_COLS

    for col in columns:
        if col not in df.columns and col != df.index.name:
            df[col] = ""

    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        df.to_excel(
            writer,
            columns=columns,
            header=True,
            index=False,
            freeze_panes=(1, 1),
            sheet_name="data",
        )
        writer.sheets['data'].set_default_row(70)
        revise = dict(BASIC_CELL_STYLE, **{
            'bg_color': '#ffffcc'
        })
        format_basic = writer.book.add_format(BASIC_CELL_STYLE)
        format_revise = writer.book.add_format(revise)

        for idx, colname in enumerate(columns):
            width = REVIEW_COL_WIDTHS.get(colname, 15)
            colc = chr(ord("A") + idx)
            fmt = format_revise if 'revised' in colname else format_basic
            writer.sheets['data'].set_column(f'{colc}:{colc}', width, fmt)


def makelist(
    notespath="./notes",
    listpath="./list.xlsx",
    names=(),
    regex=False,
    select_themes=True,
    select_stories=False,
    include_descendants=False,
    include_ancestors=False,
):
    ontology = totolo.files(notespath) if notespath else totolo.empty()

    story_ids, theme_ids = set(), set()
    if select_themes:
        conditional_add_from(ontology.themes(), names, regex, theme_ids)
    else:
        theme_ids = {t.name for t in ontology.themes()}
    if select_stories:
        conditional_add_from(ontology.stories(), names, regex, story_ids)

    extra_story_ids, extra_theme_ids = set(), set()
    if include_descendants:
        for name in story_ids:
            extra_story_ids.update(ontology.story[name].iter_descendant_names())
        for name in theme_ids:
            extra_theme_ids.update(ontology.theme[name].iter_descendant_names())
    if include_ancestors:
        for name in story_ids:
            extra_story_ids.update(ontology.story[name].iter_ancestor_names())
        for name in theme_ids:
            extra_theme_ids.update(ontology.theme[name].iter_ancestor_names())

    df = ontology.dataframe(
        subset_stories=(story_ids | extra_story_ids),
        subset_themes=(theme_ids | extra_theme_ids),
        motivation=True,
        descriptions=True,
    ).drop(
        [
            "story_description",
            "theme_definition",
            "date",
        ],
        axis=1,
    ).rename(columns={
        "story_id": "sid",
        "theme_id": "theme",
    })

    df['parents'] = [
        ', '.join(sorted(ontology.theme[t].parents))
        for t in df['theme']
    ]
    write_themelist(df, listpath)


def main():
    """
    This utility is provided as a command line script.

    Example:
        "to-makelist ./ontology/notes". mydata.xlsx -d theme1 theme2
    """
    parser = argparse.ArgumentParser(
        description=(
            'Create an excel sheet with some of the theme data from the ontology. ' +
            'If neither -t or -s are given, selects themes to include. '
        ),
        epilog=main.__doc__
    )
    parser.add_argument("path_ontology", help="Path to the ontology.")
    parser.add_argument("path_changes", help="Path to the Excel sheet file that will be written.")
    parser.add_argument('names', nargs='+', help='object names or patterns')
    parser.add_argument(
        '-t', '--themes', action='store_true', help=
        'select themes'
    )
    parser.add_argument(
        '-s', '--stories', action='store_true', help=
        'select stories'
    )
    parser.add_argument(
        '-r', '--regex', action='store_true', help=
        'names are regex patterns'
    )
    parser.add_argument(
        '-d', '--descendants', action='store_true', help=
        'also include children/descendants of selected objects'
    )
    parser.add_argument(
        '-a', '--ancestors', action='store_true', help=
        'also include parents/ancestors of selected objects'
    )
    args = parser.parse_args()
    makelist(
        notespath=args.path_ontology,
        listpath=args.path_changes,
        names=args.names,
        regex=args.regex,
        select_themes=args.themes if args.stories else True,
        select_stories=args.stories,
        include_descendants=args.descendants,
        include_ancestors=args.ancestors,
    )


if __name__ == "__main__":
    main()
