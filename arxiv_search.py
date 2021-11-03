#!/usr/bin/env python3
import os.path

import arxiv
import argparse
import logging
import csv
import sys

logging.basicConfig(level=logging.INFO)


# Command line arguments
parser = argparse.ArgumentParser(description='Arguments')
parser.add_argument('--kw', type=str, help="""Keyword to be searched. Use double quote followed by simple quote to search for an exact keyword. Example: "'exact keyword'" """)
parser.add_argument('--sort_order', default=arxiv.SortOrder.Descending, type=type(arxiv.SortOrder.Descending), help='Column to be sorted by. Default is by the columns "Citations", i.e., it will be sorted by the number of citations. If you want to sort by citations per year, use --sortby "cit/year"')
parser.add_argument('--sort_by', default=arxiv.SortCriterion.SubmittedDate, type=type(arxiv.SortCriterion.SubmittedDate), help='sort by')
parser.add_argument('--outdir', default=os.path.join(os.path.dirname(__file__), './papers'), type=str, help='output dir')
parser.add_argument('--download', action="store_true", help='enable download if True')
parser.add_argument('--nresults', default=10, type=int, help='Number of articles to search on arxiv. Default is 10. (carefull with robot checking if value is too high)')

#parser.add_argument('--csvpath', type=str, help='Path to save the exported csv file. By default it is the current folder')
#parser.add_argument('--notsavecsv', action='store_true', help='By default results are going to be exported to a csv file. Select this option to just print results but not store them')
#parser.add_argument('--plotresults', action='store_true', help='Use this flag in order to plot the results with the original rank in the x-axis and the number of citaions in the y-axis. Default is False')
#parser.add_argument('--startyear', type=int, help='Start year when searching. Default is None')
#parser.add_argument('--endyear', type=int, help='End year when searching. Default is current year')
#parser.add_argument('--debug', action='store_true', help='Debug mode. Used for unit testing. It will get pages stored on web archive')

# Parse and read arguments and assign them to variables if exists
args, _ = parser.parse_known_args()

search = arxiv.Search(
  query=args.kw,
  max_results=args.nresults,
  sort_by=args.sort_by,       # arxiv.SortCriterion.SubmittedDate,
  sort_order=args.sort_order  # sort_order = arxiv.SortOrder.Descending
)

client = arxiv.Client(
  page_size = 1000,
  delay_seconds = 10,
  num_retries = 5
)


def show_all_arxiv_structre(searchObj):
  """
  result.entry_id: A url http://arxiv.org/abs/{id}.
  result.updated: When the result was last updated.
  result.published: When the result was originally published.
  result.title: The title of the result.
  result.authors: The result's authors, as arxiv.Authors.
  result.summary: The result abstract.
  result.comment: The authors' comment if present.
  result.journal_ref: A journal reference if present.
  result.doi: A URL for the resolved DOI to an external resource if present.
  result.primary_category: The result's primary arXiv category. See arXiv: Category Taxonomy.
  result.categories: All of the result's categories. See arXiv: Category Taxonomy.
  result.links: Up to three URLs associated with this result, as arxiv.Links.
  result.pdf_url: A URL for the result's PDF if present. Note: this URL also appears among result.links.
  """

  result = [
      searchObj.entry_id,
      searchObj.updated,
      searchObj.published,
      searchObj.title,
      searchObj.authors,
      searchObj.summary,
      searchObj.comment,
      searchObj.journal_ref,
      searchObj.doi,
      searchObj.primary_category,
      searchObj.links,
      searchObj.pdf_url
  ]

  return result


def show_breif_arxiv_structre(searchObj):
  result = [
    "/".join(map(str, searchObj.authors)),
    searchObj.title,
    str(searchObj.published),
    searchObj.pdf_url,
    searchObj.summary.replace("\n", ' '),
  ]
  return result


if __name__ == '__main__':
    filename = f"{args.kw}.csv"
    write_header = False
    header = ['author', 'title', 'publish_date', 'pdf_url', 'summary']

    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    with open(filename, "w") as f:
        for result in client.results(search):
            st = show_breif_arxiv_structre(result)
            try:
                writer = csv.writer(f, delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
                if not write_header:
                    writer.writerow(header)
                    write_header = True
                writer.writerow(st)
            except csv.Error as e:
                sys.exit(f'file {filename},  {e}')

            if args.download:
                result.download_pdf(dirpath=args.outdir, filename=f"{result.title}.pdf")




