import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def text_figure(title_txt=None, subtitle_txt=None, subtitle2_txt=None, body_txt=None):
    axes = {
        1: {'txt': title_txt, 'height': .5, 'position': 0.2, 'fontsize': 50},
        2: {'txt': subtitle_txt, 'height': .1, 'position': 0.5, 'fontsize': 45},
        3: {'txt': subtitle2_txt, 'height': .1, 'position': 0.5, 'fontsize': 45},
        4: {'txt': body_txt, 'height': .3, 'position': 0.8, 'fontsize': 22}
    }
    height_ratios = tuple(axes[i]['height'] for i in axes)
    fig, (axes[1]['ax'], axes[2]['ax'], axes[3]['ax'], axes[4]['ax']) = \
        plt.subplots(nrows=4, ncols=1, figsize=(12, 8), \
                     height_ratios=height_ratios)

    for i in axes:
        axis = axes[i]
        axis['ax'].axis('off')

        if axis['txt']:
            axis['ax'].text(0.5, axis['position'], axis['txt'], fontsize=axis['fontsize'],
                            horizontalalignment='center', verticalalignment='center',
                            transform=axis['ax'].transAxes)

    fig.patch.set_facecolor('blue')

    return fig

class Report:

    def __init__(self, type, year):
        self.type = type
        self.year = str(year)

        pdf_name = f"{self.type} Report for {year}.pdf"
        self.report = PdfPages(fr'./outputs/{pdf_name}')

        self.add_cover_page()

    def add_cover_page(self):
        title_txt = f'{self.type}'
        subtitle_txt = f'{self.year}'
        subtitle2_txt = 'details'
        body_txt = 'something'
        fig = text_figure(title_txt, subtitle_txt, subtitle2_txt, body_txt)
        fig.savefig(self.report, format='pdf')


    def add_figure(self, fig):
        footer_txt = 'footer'
        fig.text(.01, .01, footer_txt, ha='left', fontsize=12, style='italic', color='grey')
        fig.savefig(self.report, format='pdf')