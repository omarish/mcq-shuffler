# -*- coding: UTF-8 -*-
import sys
import csv
import random
import click


CSV_HEADERS = "Name Tags Description Notes Answers Score".split()
MC_CHOICES = "A B C D E".split()


def parse_file(file_obj):
    reader = csv.DictReader(file_obj)
    attribute_keys = [k for k in reader.fieldnames if k in CSV_HEADERS]
    choice_keys = [k for k in reader.fieldnames if k not in CSV_HEADERS]

    parsed = []
    for row in reader:
        question = dict(row)
        attrs = {k: v for k, v in question.items() if k in attribute_keys}
        choices = {k:v for k,v in question.items() if k in choice_keys and v != ''}
        correct_answers = [x.strip() for x in row['Answers'].split(",")]
        answers = [(ch in correct_answers, choices[ch]) for ch in choices]
        attrs.update({ 'answers': answers })
        parsed.append(attrs)
    return parsed


def shuffle_answer(ans):
    random.shuffle(ans)
    zipped = [x for x in zip(MC_CHOICES, ans)]
    return dict(
        data={item[0]: item[1][1] for item in zipped},
        key=", ".join([item[0] for item in zipped if item[1][0]])
    )


def reorg_answer(row):
    shuffled = shuffle_answer(row.pop('answers'))
    del row['Answers']
    row.update(shuffled['data'])
    row.update({'Answers': shuffled['key']})
    return row


@click.command()
@click.argument('filename')
@click.option('--outfile', default=None, help='Output file (default output is stdout)')
def main(filename, outfile):
    questions = parse_file(open(filename, 'r', encoding='utf-8'))
    output = sys.stdout
    if outfile:
        # TODO: os.path.join()
        output = open(outfile, 'w', newline='', encoding='utf-8')
    writer = csv.DictWriter(
        output, fieldnames=CSV_HEADERS + MC_CHOICES, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for answer in questions:
        writer.writerow(reorg_answer(answer))


if __name__ == '__main__':
    main()
