import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages
import sql_helper as sql
import numpy as np
from expense import Expense
from payment import Payment

def text_figure(title_txt=None, subtitle_txt=None, subtitle2_txt=None, body_txt=None, color='white'):
    axes = {
        1: {'txt': title_txt, 'height': .5, 'position': 0.2, 'fontsize': 70, 'color': 'black'},
        2: {'txt': subtitle_txt, 'height': .1, 'position': 0.5, 'fontsize': 55, 'color': 'black'},
        3: {'txt': subtitle2_txt, 'height': .1, 'position': 0.5, 'fontsize': 55, 'color': 'black'},
        4: {'txt': body_txt, 'height': .3, 'position': 0.8, 'fontsize': 30, 'color': 'green'}
    }
    height_ratios = tuple(axes[i]['height'] for i in axes)
    fig, (axes[1]['ax'], axes[2]['ax'], axes[3]['ax'], axes[4]['ax']) = \
        plt.subplots(nrows=4, ncols=1, figsize=(12, 8), \
                     height_ratios=height_ratios)

    for i in axes:
        axis = axes[i]
        axis['ax'].axis('off')

        if axis['txt']:
            axis['ax'].text(0.5, 
                            axis['position'], 
                            axis['txt'],
                            fontsize=axis['fontsize'],
                            color=axis['color'],
                            horizontalalignment='center', 
                            verticalalignment='center',
                            transform=axis['ax'].transAxes)

    fig.patch.set_facecolor(color)
    plt.close(fig)

    return fig

class Report:

    def __init__(self, year):
        self.year = year

        pdf_name = f"Revenue Report for {str(year)}.pdf"
        self.report = PdfPages(fr'./outputs/{pdf_name}')

        self.df_dict = {
            'transactions': sql.get_all_transactions(),
            'expenses': Expense.get_dataframe(),
            'payments': Payment.get_dataframe_w_unit()
        }

        for type in self.df_dict:
            df = self.df_dict[type]

            df['Date'] = pd.to_datetime(df['Date'])
            df['Year'] = df['Date'].dt.year
            self.df_dict[type] = df[df['Year'] <= self.year]

        self.units = self.df_dict['transactions']['Unit'].unique()

        self.add_cover_page()

    def add_cover_page(self):
        params = {
            'title_txt': f'Revenue Report',
            'subtitle2_txt': f'{str(self.year)}',
        }
        fig = text_figure(**params)
        fig.savefig(self.report, format='pdf')
        plt.close(fig)

    def add_section_cover(self, section, descr):
        params = {
            'subtitle_txt': section,
            'body_txt': descr
        }
        fig = text_figure(**params)
        fig.savefig(self.report, format='pdf')
        plt.close(fig)

    def add_figure(self, fig):
        footer_txt = f'Revenue Report - {str(self.year)}'
        fig.text(.01, .01, footer_txt, ha='left', fontsize=12, style='italic', color='grey')
        fig.savefig(self.report, format='pdf')
        plt.close(fig)

    def add_transaction_bar(self):

        df = self.df_dict['transactions'].copy()

        df_filtered = df[df['Date'].dt.year == self.year]
        
        df_pivot = df_filtered.pivot_table(index='Unit', columns='Type', values='Amount', aggfunc='sum')
        df_pivot /= 1000

        try:
            df_pivot['net'] = df_pivot['payment'] - df_pivot['expense']
        except:
            pass

        unit_labels = [f"Unit {str(unit)}" for unit in df_pivot.index]
        colors = {'expense': 'red', 'payment': 'green', 'net': 'blue'}

        x = np.arange(len(unit_labels))

        nbars = 3
        bsize = 0.25
        midbar = (nbars+1)/2
        left_shift = -bsize*(midbar-1)
        offset = left_shift

        fig, ax = plt.subplots(figsize=(12,8))

        for column in df_pivot.columns:
            plt.bar(x + offset, df_pivot[column], bsize, label=column, color=colors[column])
            offset = offset + bsize

        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))

        ax.set_ylabel('Amount (in $1,000s)')
        ax.set_title('Transactions by Unit', fontsize=20)
        ax.set_xticks(x + bsize + left_shift, unit_labels)
        ax.legend(loc='upper left', ncols=2)

        self.add_figure(fig)
        plt.close(fig)

        return fig
    

    def transaction_line_subplot(self, ax, unit='all'):

        df = self.df_dict['transactions'].copy()

        df_filtered = df[df['Year'] <= self.year]
        df_unit = df_filtered if unit=='all' else df_filtered[df_filtered['Unit']==unit]
        df_pivot = df_unit.pivot_table(index='Year', columns='Type', values='Amount', aggfunc='sum')

        df_pivot /= 1000
        try:
            df_pivot['net'] = df_pivot['payment'] - df_pivot['expense']
        except:
            pass

        colors = {'expense': 'red', 'payment': 'green', 'net': 'blue'}

        for column in df_pivot.columns:
            ax.plot(df_pivot.index, df_pivot[column], label=column, color=colors[column])
        
        ax.set_ylabel('Amount (in $1,000s)')
        ax.set_title('Transactions by Year', fontsize=20 if unit=='all' else 12)
        ax.legend(loc='upper left', ncols=2)

        ax.set_xticks(df_pivot.index)
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))

        return ax
    
    def transaction_pie_subplot(self, ax, unit='all'):
        df = self.df_dict['transactions'].copy()

        df_filtered = df[df['Year'] == self.year]
        df_unit = df_filtered if unit=='all' else df_filtered[df_filtered['Unit']==unit]
        df_agg = df_unit.groupby('Type')['Amount'].sum()

        colors = {'expense': 'red', 'payment': 'green'}

        wedges, texts, autotexts = ax.pie(df_agg, autopct='%1.1f%%', startangle=90, colors=[colors.get(type, 'gray') for type in df_agg.index])

        ax.set_title('Transactions by Type', fontsize=20 if unit=='all' else 12)
        ax.axis('equal')
        ax.legend(wedges, df_agg.index, title="Transaction Type", loc="upper left", ncol=1)

        return ax
    
    def expense_pie_subplot(self, ax, unit='all'):
        df = self.df_dict['expenses'].copy()

        df_filtered = df[df['Year'] == self.year]
        df_unit = df_filtered if unit=='all' else df_filtered[df_filtered['Unit ID']==unit]
        df_agg = df_unit.groupby('Description')['Amount'].sum()

        wedges, texts, autotexts = ax.pie(df_agg, autopct='%1.1f%%', startangle=90)

        ax.set_title('Expenses by Type', fontsize=20 if unit=='all' else 12)
        ax.axis('equal')
        ax.legend(wedges, df_agg.index, title="Expense Type", loc="best", ncol=1)

        return ax
    
    def payment_pie_subplot(self, ax, unit='all'):

        df = self.df_dict['payments'].copy()

        df_filtered = df[df['Year'] == self.year]
        df_unit = df_filtered if unit=='all' else df_filtered[df_filtered['Unit ID']==unit]
        df_agg = df_unit.groupby('Payment Type')['Amount'].sum()

        wedges, texts, autotexts = ax.pie(df_agg, autopct='%1.1f%%', startangle=90)

        ax.set_title('Payments by Type', fontsize=20 if unit=='all' else 12)
        ax.axis('equal')
        ax.legend(wedges, df_agg.index, title="Payment Type", loc="best", ncol=1)

        return ax
    
    def add_subplots(self):
        subplot_functions = [
            self.transaction_line_subplot,
            self.transaction_pie_subplot,
            self.expense_pie_subplot,
            self.payment_pie_subplot
        ]

        for func in subplot_functions:
            fig, ax = plt.subplots(figsize=(12,8))
            ax = func(ax)
            self.add_figure(fig)
            plt.close(fig)
    
    def indiv_unit_charts(self, unit):
        ax = {}

        fig, ((ax[(0, 0)], ax[(0, 1)]), (ax[(1, 0)], ax[(1, 1)]), (ax[2, 0], ax[(2, 1)])) = \
            plt.subplots(nrows=3, ncols=2, figsize=(12, 8), \
                        width_ratios=(.5,.5), height_ratios=(.1, .45,.45))
        
        ax[(0, 0)].axis('off')
        ax[(0, 1)].axis('off')
        ax[(0, 0)].text(0.5, 0.5, f"Unit {str(unit)} Performance", fontsize=30,
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax[(0, 0)].transAxes)
        
        ax[(1, 0)] = self.transaction_line_subplot(ax[(1, 0)], unit)
        ax[(1, 1)] = self.transaction_pie_subplot(ax[(1, 1)], unit)
        ax[(2, 0)] = self.expense_pie_subplot(ax[(2, 0)], unit)
        ax[(2, 1)] = self.payment_pie_subplot(ax[(2, 1)], unit)

        fig.tight_layout()
    
        self.add_figure(fig)
        plt.close(fig)

        return fig
    

def generate_income_report(year):
    rpt = Report(year)

    rpt.add_section_cover('All Units', 'Analytics for aggregated unit data')
    rpt.add_transaction_bar()
    rpt.add_subplots()

    rpt.add_section_cover('Individual Units', 'Analytics for individual rental units')
    for unit in rpt.units:
        rpt.indiv_unit_charts(unit)
    rpt.report.close()