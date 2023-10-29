#!/usr/bin/env python
import sys

from Currency import Currency
from Graph import Graph
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from pathlib import Path

cwd = Path(__file__).parent.resolve()
data_folder = cwd.parent / 'data'


def set_graph(df):
    graph = Graph(df)
    graph.set_main_label("Date")
    graph.mark_graph(stat="median", color="b")
    graph.mark_graph(stat="max", color="g")
    graph.mark_graph(stat="min", color="r")
    graph.mark_graph(stat="mean", color="black")
    graph.show_graph()


def main():
    currency = Currency(sep=";", decimal=",")
    currency.get_all_currency_data()

    selected_currency = inquirer.checkbox(
        message="Select exchange rates",
        choices=[
            Choice("CHF/PLN", name="CHF to PLN"),
            Choice("USD/PLN", name="USD to PLN"),
            Choice("EUR/PLN", name="EUR to PLN"),
            Choice("CHF/USD", name="CHF to USD"),
            Choice("EUR/USD", name="EUR to USD"),
        ],
        validate=lambda result: len(result) >= 1,
        invalid_message="Select at least 1 exchange rate",
        instruction="(Select at least 1)",
        transformer=lambda _: ""
    ).execute()

    df = currency.get_selected_currency_data(selected_currency)

    print(f"Data for {', '.join(selected_currency)} has been save to {data_folder}/selected_currency_data.csv")

    visualize_data = inquirer.select(
        message="Do you want to see this data now?",
        choices=[
            Choice(True, name="Yes"),
            Choice(False, name="No")
        ]
    ).execute()

    if not visualize_data:
        sys.exit(0)

    set_graph(df)


if __name__ == '__main__':
    main()
