#
# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#/

#
# Zeroth (no code changes necessary) in a series of exercises in a gaming domain.
#
# <p>This batch pipeline imports game events from CSV to BigQuery.
#
# <p>See README.md for details.
#

import argparse
import parser
import sys

import apache_beam as beam
from apache_beam.io import WriteToBigQuery
from apache_beam.io.gcp.internal.clients.bigquery import TableSchema, TableFieldSchema
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
import utils.parse_event_fn


def table_field(name, type):
    name_field = TableFieldSchema()
    name_field.name = name
    name_field.type = type
    return name_field

def table_schema():
    table_schema = TableSchema()
    table_schema.fields = [
        table_field('user', 'STRING'),
        table_field('team', 'STRING'),
        table_field('score', 'INTEGER'),
        table_field('timestamp', 'INTEGER')
    ]
    return table_schema


def main(argv):
    """Main entry point; defines and runs the user_score pipeline."""
    parser = argparse.ArgumentParser()

    parser.add_argument('--input',
        type=str,
        default='',
        help='Path to the data file(s) containing game data.')

    parser.add_argument('--output_dataset',
        type=str,
        default='',
        help='The BigQuery dataset name where to write all the data.')

    parser.add_argument('--output_table_name',
        type=str,
        default='',
        help='The BigQuery table name where to write all the data.')

    args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(pipeline_args)

    with beam.Pipeline(options=options) as p:
        (p  | 'ReadInputText' >> beam.io.ReadFromText(args.input)
            | 'ParseGameEvent' >> beam.ParDo(utils.parse_event_fn.processElement)
            | 'WriteTeamScoreSums' >> WriteToBigQuery(
                args.output_table_name, args.output_dataset, options.get_all_options().get("project"), table_schema()
              )
         )

if __name__ == "__main__":
    main(sys.argv)