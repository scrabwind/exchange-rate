import requests
from requests import HTTPError, Timeout, RequestException, ConnectionError
import pandas as pd
import numpy as np
import logging
from pathlib import Path

cwd = Path(__file__).parent.resolve()
data_folder = cwd.parent / 'data'


class _CurrencyAPI:
    @staticmethod
    def get_exchange_rate_data(currency):
        """Get exchange rates from API and return DataFrame"""

        table = "a"
        res_format = "json"
        base_url = "https://api.nbp.pl/api/exchangerates/rates"

        url = f"{base_url}/{table}/{currency}/last/{last_days}/?format={res_format}"

        try:
            res = requests.get(url)
            body = res.json()
            return body
        except ConnectionError as error:
            logging.critical(f"There was an connection error: {error}")
            raise
        except HTTPError as error:
            logging.critical(f"Request failed with status code: {error}")
            raise
        except Timeout:
            logging.critical("Request timeout")
            raise
        except RequestException as error:
            logging.critical(f"Something went wrong with request: {error}")
            raise


class _CurrencyFileManager:
    @staticmethod
    def set_all_currency_data(file_name, dataframe, *, sep, decimal):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Passed argument is not DataFrame")
        if not file_name:
            raise ValueError("file_name has not been set")
        if not sep:
            raise ValueError("sep has not been set")
        if not decimal:
            raise ValueError("decimal has not been set")
        try:
            dataframe.to_csv(
                f"{data_folder}/{file_name}",
                sep=sep,
                decimal=decimal
            )
        except PermissionError as e:
            logging.critical("Program was not permitted to save/overwrite file")
            raise OSError from e

    @staticmethod
    def get_all_currency_data(file_name, *, sep, decimal):
        try:
            dataframe = pd.read_csv(
                f"{data_folder}/{file_name}",
                sep=sep,
                decimal=decimal,
                index_col="Date"
            )
            return dataframe
        except FileNotFoundError:
            logging.error("Couldn't read file")
            raise

    @staticmethod
    def set_selected_currency_data(file_name, dataframe, selected_currency, *, sep, decimal):
        if len(selected_currency) == 0:
            raise ValueError(f"No currency have been selected")

        try:
            selected_df = dataframe[
                dataframe.columns.intersection(selected_currency)
            ]
            selected_df.to_csv(
                f"{data_folder}/{file_name}",
                sep=sep,
                decimal=decimal
            )
        except Exception:
            raise

    @staticmethod
    def get_selected_currency_data(file_name, *, sep, decimal):
        index_col = "Date"
        if not file_name:
            raise ValueError("file_name has not been set")
        if not sep:
            raise ValueError("sep has not been set")
        if not decimal:
            raise ValueError("decimal has not been set")
        try:
            selected_currency = pd.read_csv(
                f"{data_folder}/{file_name}",
                sep=sep,
                decimal=decimal,
                index_col=index_col
            )
            return selected_currency
        except FileNotFoundError:
            logging.critical("Couldn't read file")
            raise

    @staticmethod
    def update_data():
        currency_api = ["chf", "usd", "eur"]
        map(_CurrencyAPI.get_exchange_rate_data, currency_api)
        pass


class _CurrencyFormatter:
    @staticmethod
    def format_data(json_data):
        """format JSON data to DataFrame"""
        expected_keys = np.array(["table", "currency", "code", "rates"])
        json_keys = np.array(json_data.keys())

        if np.array_equal(expected_keys, json_keys):
            raise ValueError(f"JSON data have wrong keys."
                             f"\nExpected keys: {', '.join(expected_keys)}"
                             f"\nProvided keys: {', '.join(json_keys)}")

        rates = json_data["rates"]
        df = pd.DataFrame(rates)

        index = df["effectiveDate"]
        column = f"{json_data['code']}/PLN"

        df.drop(columns=["no", "effectiveDate"], inplace=True)

        df.index = pd.to_datetime(index)
        df.columns = [column]
        df.index.name = "Date"

        return df

    @staticmethod
    def add_exchange_rate(dataframe, numerator, denominator, output_column_name, inplace=False):
        """
        Create exchange rate for CHF/USD and EUR/USD based on other exchange rates
        Using inplace to override dataframe instead of copying and returning it
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Passed param is not dataframe")
        if not inplace:
            dataframe = dataframe.copy()

        df = dataframe
        df[output_column_name] = df[numerator].divide(df[denominator])

        if inplace:
            return None
        return df


class Currency:
    _instance = None
    _CURRENCY_API_VALUES = ["chf", "usd", "eur"]

    def __init__(self, sep=",", decimal=".", all_file_name="all_currency_data.csv",
                 selected_file_name="selected_currency_data.csv"):
        """Initialize instance and fetch exchange rates from API and convert them to one dataframe"""
        self.all_df = None
        self.sep = sep
        self.decimal = decimal
        self.all_file_name = all_file_name
        self.selected_file_name = selected_file_name

    def _set_currency(self, currency=None):
        json_responses = map(_CurrencyAPI.get_exchange_rate_data, self._CURRENCY_API_VALUES)
        json_responses = list(json_responses)
        dataframes = map(_CurrencyFormatter.format_data, json_responses)
        dataframes = list(dataframes)
        dataframes = pd.concat(dataframes, axis=1)
        self.all_df = dataframes
        # Add missing exchange rates based on previously fetched ones
        _CurrencyFormatter.add_exchange_rate(
            self.all_df,
            "EUR/PLN",
            "USD/PLN",
            "EUR/USD",
            inplace=True
        )
        _CurrencyFormatter.add_exchange_rate(
            self.all_df,
            "CHF/PLN",
            "USD/PLN",
            "CHF/USD",
            inplace=True
        )

        if not currency:
            _CurrencyFileManager.set_all_currency_data(self.all_file_name, self.all_df, sep=self.sep,
                                                       decimal=self.decimal)
        else:
            _CurrencyFileManager.set_selected_currency_data(self.selected_file_name, self.all_df, currency,
                                                            sep=self.sep,
                                                            decimal=self.decimal)

    def get_selected_currency_data(self, currency):
        self._set_currency(currency=currency)
        return _CurrencyFileManager.get_selected_currency_data(self.selected_file_name, decimal=self.decimal,
                                                               sep=self.sep)

    def get_all_currency_data(self):
        self._set_currency()
        data = _CurrencyFileManager.get_all_currency_data(self.all_file_name, decimal=self.decimal, sep=self.sep)
        return data
