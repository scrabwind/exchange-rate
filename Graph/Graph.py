import logging

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np


class Graph:
    def __init__(self, dataframe):
        self.df = dataframe
        self.df.index = pd.to_datetime(self.df.index)
        self.axes = self.df.plot(subplots=True, x_compat=True)
        self._init_graph_format()

    def _init_graph_format(self):
        for ax in self.axes:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    def set_main_label(self, label):
        axes_label = label
        if not isinstance(axes_label, str):
            logging.warning("Passed label is no string")
            axes_label = ""
        self.axes[-1].set_label(label)

    def mark_graph(self, stat="mean", color="r"):
        for ax, col in zip(self.axes, self.df.columns):

            value = None
            match stat:
                case "mean":
                    value = self.df[col].mean()
                    ax.axhline(value, color=color, linestyle="--")
                    ax.text(0.95, value, f'{stat}: {value:.2f}', verticalalignment='bottom',
                            horizontalalignment='left',
                            transform=ax.get_yaxis_transform(), color=color)

                case "median":
                    value = self.df[col].median()
                    ax.axhline(value, color=color, linestyle="--")
                    ax.text(0.95, value, f'{stat}: {value:.2f}', verticalalignment='bottom',
                            horizontalalignment='right',
                            transform=ax.get_yaxis_transform(), color=color)
                case "max":
                    value_idx = self.df[col].idxmax()
                    value = self.df[col].max()
                    # ax.scatter([value_idx], [value], color=color, zorder=5)
                    ax.annotate(f"Max: {value:.2f}", (value_idx, value))
                case "min":
                    value_idx = self.df[col].idxmin()
                    value = self.df[col].min()
                    ax.annotate(f"Min: {value:.2f}", (value_idx, value))
                case _:
                    logging.error("specified stat didn't match one of the following: mean, median, max, min")
            # ax.text(0.95, value, f'{stat}: {value:.2f}', verticalalignment='bottom', horizontalalignment='right',
            #         transform=ax.get_yaxis_transform(), color=color)
            # ax.table(cellText=[["1", "2", "3"], ["1", "2", "3"]])

    @staticmethod
    def show_graph():
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.draw()
        plt.show()
