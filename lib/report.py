import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.transforms import Bbox
from matplotlib.backends.backend_pdf import PdfPages
import sql_helper as sql
import numpy as np
from expense import Expense
from payment import Payment
from functools import partial

def text_figure(title_txt=None, subtitle_txt=None, subtitle2_txt=None, body_txt=None, 
                font_color='black', color='white', background=None):
    '''
    A class to create and manage pdf revenue reports

    Parameters
    ---------
    title_txt (optional): str
        - title of page
    subtitle_txt (optional): str
        - subtitle of page
    subtitle2_txt (optional): str
        - subtitle2 of page
    body_txt (optional): str
        - body of page
    color (optional): str
        - color of page

    Returns
    ---------
    fig: matplotly figure
        - figure containing text only for report cover pages
    '''
    axes = {
        1: {'txt': title_txt, 'height': .5, 'position': 0.2, 'fontsize': 80},
        2: {'txt': subtitle_txt, 'height': .1, 'position': 0.5, 'fontsize': 80},
        3: {'txt': subtitle2_txt, 'height': .1, 'position': 0.5, 'fontsize': 80},
        4: {'txt': body_txt, 'height': .3, 'position': 0.8, 'fontsize': 30}
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
                            color=font_color,
                            horizontalalignment='center', 
                            verticalalignment='center',
                            transform=axis['ax'].transAxes)

    fig.patch.set_facecolor(color)

    if background:
        img = plt.imread(background)
        background_ax = fig.add_axes([0, 0, 1, 1], zorder=-1)
        background_ax.imshow(img, aspect='auto', extent=[0, 1, 0, 1])
        background_ax.axis('off')

    plt.close(fig)

    return fig

class Report:
    '''
    A class to create and manage pdf revenue reports

    Attributes
    ---------
    year: int
        - year for report
    report: PdfPages instance
        - instance of pdf report
    units: list
        - list of units with transactions for specified year

    Methods
    ---------
    - add_cover_page: creates cover page and adds to report
    - add_section_cover: creates section cover and adds to report
    - add_figure: adds matplotly figure as a page to report
    - group_data_for_year: groups data by specified year and column
    - transaction_totals_annotation: creates figure showing transaction totals by type
    - add_transaction_bar: creates bar graph of transactions and adds to report
    - transaction_line_subplot: creates line graph of transactions
    - transaction_pie_subplot: creates pie chart by category for specified transaction type
    - add_subplots: creates separate pages for each subplot and adds to report
    - indiv_unit_charts: creates page for specified unit with subplots and adds to report
    '''
    def __init__(self, year, path):
        '''
        Constructs the necessary attributes for the Report object.

        Parameters
        ---------
        year: int
            - year for report
        '''
        self.year = year
        self.report = PdfPages(path)

        self.df_dict = {
            'transactions': sql.get_all_transactions(),
            'expenses': Expense.get_dataframe(),
            'payments': Payment.get_dataframe_w_unit()
        }

        for type in self.df_dict:
            df = self.df_dict[type]

            df['Date'] = pd.to_datetime(df['Date'])
            df['Year'] = self.df_dict[type]['Date'].dt.year
            self.df_dict[type] = df[df['Year'] <= self.year]

        self.units = self.df_dict['transactions']['Unit'].unique()

        self.add_cover_page()

    def add_cover_page(self):
        '''
        creates cover page and adds to report
        '''
        params = {
            'title_txt': f'Revenue Report',
            'subtitle2_txt': f'{str(self.year)}',
            'font_color': 'white',
            'background': './img/blue_background.jpg'
        }
        fig = text_figure(**params)
        fig.savefig(self.report, format='pdf')
        plt.close(fig)

    def add_section_cover(self, section, descr):
        '''
        creates section cover and adds to report
        '''
        params = {
            'subtitle_txt': section,
            'body_txt': descr,
            'font_color': '#141919',
            'background': './img/section_cover.png'
        }
        fig = text_figure(**params)
        fig.savefig(self.report, format='pdf')
        plt.close(fig)

    def add_figure(self, fig):
        '''
        adds matplotly figure as a page to report

        Parameters
        ---------
        fig: matplotly figure
            - figure to add to report
        '''
        footer_txt = f'Revenue Report - {str(self.year)}'
        fig.text(.01, .01, footer_txt, ha='left', fontsize=12, style='italic', color='grey')
        fig.savefig(self.report, format='pdf')
        plt.close(fig)

    def group_data_for_year(self, df, col_to_group, unit='all'):
        '''
        groups data by specified year and column

        Parameters
        ---------
        df: Pandas DataFrame
            - initial data to be grouped
        col_to_group: str
            - name of column in dataframe to group by
        unit (optional): int or str
            - unit ID to filter data on

        Returns
        ---------
        df_agg: Pandas DataFrame
            - data grouped by specified year, column and optionally filtered on unit
        '''
        df_filtered = df[df['Year'] == self.year]
        df_unit = df_filtered if unit=='all' else df_filtered[df_filtered['Unit']==unit]
        df_agg = df_unit.groupby(col_to_group)['Amount'].sum()

        return df_agg

    def transaction_totals_annotation(self, ax, unit='all'):
        '''
        creates figure showing transaction totals by type

        Parameters
        ---------
        ax: matplotly figure
            - blank figure
        unit (optional): int or str
            - unit ID to filter data on

        Returns
        ---------
        ax: matplotly figure
            - annotation showing transaction totals by type (payment, expense, net)
        '''
        df = self.df_dict['transactions']
        df_agg = self.group_data_for_year(df, 'Type', unit)

        # Calculate totals
        total_income = df_agg.get('payment', 0)
        total_expenses = df_agg.get('expense', 0)
        net_income = total_income - total_expenses  # Expenses are negative in the data

        # Add totals as a label
        summary_text = (
            f"Total Income: ${total_income:,.0f}\n"
            f"Total Expenses: ${total_expenses:,.0f}\n"
            f"Net Income: ${net_income:,.0f}"
        )
        ax.text(
            1.1, 0, summary_text,
            transform=ax.transAxes,
            fontsize=10,
            fontweight='bold',
            horizontalalignment='right',
            bbox=dict(facecolor='white', alpha=0.5, edgecolor='gray')
        )

        return ax

    def add_transaction_bar(self):
        '''
        creates bar graph of transactions and adds to report

        Returns
        ---------
        fig: matplotly figure
            - bar graph of transactions
        '''
        df = self.df_dict['transactions'].copy()

        df_filtered = df[df['Year'] == self.year]
        
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
        '''
        creates line graph of transactions with points for data

        Parameters
        ---------
        ax: matplotly figure
            - blank figure
        unit (optional): int or str
            - unit ID to filter data on

        Returns
        ---------
        ax: matplotly figure
            - line graph of transactions
        '''
        df = self.df_dict['transactions'].copy()

        df_unit = df if unit == 'all' else df[df['Unit'] == unit]
        df_pivot = df_unit.pivot_table(index='Year', columns='Type', values='Amount', aggfunc='sum')

        df_pivot /= 1000
        try:
            df_pivot['net'] = df_pivot['payment'] - df_pivot['expense']
        except:
            pass

        colors = {'expense': 'red', 'payment': 'green', 'net': 'blue'}

        for column in df_pivot.columns:
            ax.plot(df_pivot.index, df_pivot[column], label=column, color=colors[column])
            ax.scatter(df_pivot.index, df_pivot[column], color=colors[column], edgecolor='black', s=50)  # Add points

        ax.set_ylabel('Amount (in $1,000s)')
        ax.set_title('Transactions by Year', fontsize=20 if unit == 'all' else 12)
        ax.legend(
            title="Transaction Type",
            loc='upper left',
            ncol=1
        )

        ax.set_xticks(df_pivot.index)
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))

        return ax
        
    def transaction_pie_subplot(self, ax, ttype, unit='all'):
        '''
        creates pie chart by category for specified transaction type

        Parameters
        ---------
        ax: matplotly figure
            - blank figure
        ttype: str
            - transaction type (expenses, payments)
        unit (optional): int or str
            - unit ID to filter data on

        Returns
        ---------
        ax: matplotly figure
            - pie chart of payments
        '''
        df = self.df_dict[ttype].copy()
        groupby = 'Type' if ttype=='transactions' else 'Category'
        df_agg = self.group_data_for_year(df, groupby, unit)
        df_agg = df_agg.sort_values(ascending=False)

        kwargs = {
            'autopct': '%1.1f%%', 
            'startangle': 90
        }

        if ttype == 'transactions':
            colors = {'expense': 'red', 'payment': 'green', 'net': 'blue'}
            color_list = [colors.get(type, 'gray') for type in df_agg.index]
            kwargs['colors'] = color_list

        wedges, texts, autotexts = ax.pie(df_agg, **kwargs)
        
        # Hide labels for small slices
        for i, autotext in enumerate(autotexts):
            # Only show the label if the percentage is greater than or equal to threshold
            if df_agg.iloc[i] / df_agg.sum() * 100 < 5:
                autotext.set_text('')  # Hide the label

        ax.set_title(
            f'{ttype.title()} by {groupby}', 
            fontsize=20 if unit=='all' else 12
            )
        ax.axis('equal')
        ax.legend(
            wedges, 
            df_agg.index, 
            title=groupby, 
            loc='upper right', 
            bbox_to_anchor=(1.1, 1),
            ncol=1
            )

        return ax
    
    def add_subplots(self):
        '''
        creates separate pages for each subplot and adds to report
        '''
        subplot_functions = [
            self.transaction_totals_annotation,
            self.transaction_line_subplot,
            partial(self.transaction_pie_subplot, ttype='transactions'),
            partial(self.transaction_pie_subplot, ttype='payments'),
            partial(self.transaction_pie_subplot, ttype='expenses')
        ]

        for func in subplot_functions:
            fig, ax = plt.subplots(figsize=(12,8))
            ax = func(ax=ax)
            self.add_figure(fig)
            plt.close(fig)
    
    def indiv_unit_charts(self, unit='all'):
        '''
        creates page for specified unit with subplots and adds to report

        Parameters
        ---------
        unit (optional): int or str
            - unit ID to filter data on

        Returns
        ---------
        fig: matplotly figure
            - figure containing multiple graphs for specified unit
        '''
        title = f"Unit {str(unit)} Analytics" if unit != 'all' else "Analytics for All Units"
        ax = {}

        fig, ((ax[(0, 0)], ax[(0, 1)]), (ax[(1, 0)], ax[(1, 1)]), (ax[2, 0], ax[(2, 1)])) = \
            plt.subplots(nrows=3, ncols=2, figsize=(12, 8), \
                        width_ratios=(.5,.5), height_ratios=(.1, .45,.45))
        
        ax[(0, 0)].axis('off')
        ax[(0, 0)].text(0, .5, title, fontsize=30, fontweight='bold',
                    horizontalalignment='left', verticalalignment='center',
                    transform=ax[(0, 0)].transAxes)
        
        ax[(0, 1)].axis('off')
        ax[(0, 1)] = self.transaction_totals_annotation(ax[(0, 1)], unit)
        
        ax[(1, 0)] = self.transaction_line_subplot(ax[(1, 0)], unit)
        ax[(1, 1)] = self.transaction_pie_subplot(ax[(1, 1)], 'transactions', unit)
        ax[(2, 0)] = self.transaction_pie_subplot(ax[(2, 0)], 'payments', unit)
        ax[(2, 1)] = self.transaction_pie_subplot(ax[(2, 1)], 'expenses', unit)

        # fig.tight_layout()
        fig.subplots_adjust(hspace=0.5, wspace=0)
    
        self.add_figure(fig)
        plt.close(fig)

        return fig

def generate_income_report(year, path):
    '''
    generates and saves pdf report for specified year using Report class

    Parameters
    ---------
    year: int
        - year for report
    path: str
        - file path to save report
    '''
    rpt = Report(year, path)

    rpt.add_section_cover('All Units', 'Analytics for aggregated unit data')
    rpt.add_transaction_bar()

    rpt.indiv_unit_charts()

    rpt.add_section_cover('Individual Units', 'Analytics for individual rental units')
    for unit in rpt.units:
        rpt.indiv_unit_charts(unit)
    rpt.report.close()