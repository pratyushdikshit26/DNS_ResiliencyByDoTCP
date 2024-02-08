from matplotlib.backends.backend_pdf import PdfPages


class PlotSaver:
    BASE_DIR = ""
    current_path = ""
    def __init__(self, base_dir):
        self.BASE_DIR = base_dir
    
    def save_figure(self, fig, name):
        fig.savefig(self.BASE_DIR + self.current_path + name, bbox_inches='tight')

    def save_table(self, df, name):
        df.to_csv(self.BASE_DIR + self.current_path + name)
