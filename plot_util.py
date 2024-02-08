import math
from matplotlib.ticker import FuncFormatter
import seaborn as sns

def get_plot_index(plot_number, ncols = 2):
    column = plot_number % ncols
    row = math.floor(plot_number/ncols)
    return row, column


def plot_heatmap(data, axs, plot_count, is_diff = False, is_asn = False, is_cont = False, is_failure_rate = False):
    ax = axs[get_plot_index(plot_count,3)]
    cmap = "RdYlGn_r" if not is_diff else 'RdBu_r'
    if is_failure_rate:
        vmin = 0 if not is_diff else -0.2
        vmax = 0.25 if not is_diff else 0.2
        fmt='.5%'
        cbar_kws = {'label' : 'Failure Rate', 'format': FuncFormatter(lambda x, pos: '{:.5%}'.format(x))}
    else:
        vmin = 0 if not is_diff else -200
        vmax = 500 if not is_diff else 200
        fmt='g'
        cbar_kws = {'label' : 'Failure Rate'}

    sns.heatmap(data,  
                fmt=fmt,  
                annot=True,
                cbar=is_asn,
                cmap=cmap,
                cbar_kws = cbar_kws,
                ax = ax,
                vmin=vmin,
                vmax=vmax)
    if not is_diff:
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticklabels([])
        if is_asn or is_cont:
            ax.set_yticklabels([])
    else:
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        if is_asn or is_cont:
            ax.set_yticklabels([])