# Imports Alphabetically:
from decimal import Decimal
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from os import listdir
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from scipy import stats
from scipy.interpolate import interp1d
from scipy.optimize import fmin
from scipy.optimize import fsolve
from textwrap import dedent as d
import base64
import datetime
import glob
import io
import math
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import plotly.graph_objs as go
import plotly.offline
import sys
import wx
import wx.html
import wx.lib.agw.multidirdialog as MDD
import wx.lib.scrolledpanel as scrolled
matplotlib.use('WXAgg')

# This is a text to be used in a "About" menu button:
aboutText = "<p>This program is a part of Luscombe Group OPV Analysis project \
in University of Washington, Seattle. It is running on version %(wxpy)s \
of <b>wxPython</b> and %(python)s of <b>Python</b>. \
See <a href='http://wiki.wxpython.org'>wxPython Wiki</a></p> for more \
information about this platform."

flags = [1, 1, 1, 1, 1, 1, 1, 1]  # global variable


# Defining a basic panel:
class panel(wx.Panel):
    def __init__(self, parent, data, vals, number):
        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_SUNKEN,
                          size=(500, 350))

        self.SetMinSize((500, 350))
        self.SetBackgroundColour("#b7a57a")
        self.num = number  # This will serve as an index for our plots

        # Defining data for plots:
        PCE = vals[0]
        VocL = vals[1]
        JscL = vals[2]
        FF = vals[3]
        datas = [PCE, VocL, JscL, FF]  # these are our parameters
        n_rows = len(datas)
        rows = ['$PCE\ [\%]$', '$V_{OC}\ [V]$', '$J_{SC}\ [mA/cm^2]$',
                '$FF\ [\%]$']
        cell_text = []  # this list will hold the values for the parameters
        for row in range(n_rows):
            if row != 1:
                cell_text.append(['%1.1f' % datas[row]])
            else:
                cell_text.append(['%1.2f' % datas[row]])

        # Rearranging the data for the table next to the plot:
        flat_list = []
        for sublist in cell_text:
            for item in sublist:
                flat_list.append(item)
        tabledata = list(zip(rows, flat_list))

        # Plotting:
        self.figure, self.axes = plt.subplots(figsize=(4, 4),
                                              facecolor='gainsboro')
        mpl.rc('axes', linewidth=2)
        plt.tight_layout(h_pad=1.0)
        plt.subplots_adjust(bottom=0.18)

        # This is the JV curve drawn from the actual data:
        self.axes.plot(data[:, 0], data[:, 2], linewidth=2, zorder=4)

        # This is to highlight x-Axis on the plot area:
        self.axes.plot([-0.2, 0.8], [0, 0], color='k', linestyle='-',
                       linewidth=2, zorder=2)

        # This is to highlight y-Axis on the plot area:
        self.axes.plot([0, 0], [-5, 20], color='k', linestyle='-',
                       linewidth=2, zorder=3)

        # Plot design:
        self.axes.set_xlabel('$Voltage\ [V]$')
        self.axes.set_ylabel('$Current\ Density\ [mA/cm^2]$')
        self.axes.set_xlim([-0.2, 0.8])
        self.axes.set_ylim([-5, 20])
        self.axes.minorticks_on()
        self.axes.tick_params(which='major', axis='both', width=1, length=5)
        self.axes.tick_params(which='minor', axis='both', width=1, length=2)
        self.axes.grid(which='major', axis='both', color='grey',
                       linestyle='--', linewidth=1, zorder=1)

        # Adding a table to the plot:
        cellcolors = [['#b7a57a', 'w'], ['#b7a57a', 'w'], ['#b7a57a', 'w'],
                      ['#b7a57a', 'w']]
        self.axes.table(cellText=tabledata,
                        cellLoc='center', cellColours=cellcolors,
                        bbox=[0.25, 0.5, 0.5, 0.4], zorder=5)

        # Defining sizer:
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Defining the whole plotting area:
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer.Add(self.canvas, 1, wx.ALL | wx.ALIGN_TOP | wx.EXPAND)

        # Defining a plotly plot for zoomed window:
        self.fig = go.Figure()
        self.fig.add_scatter(x=data[:, 0],
                             y=data[:, 2],
                             mode='lines+markers',
                             name='JV Curve',
                             marker_color='rgba(51, 0, 111, 0.2)',
                             marker_size=10,
                             marker_line_width=2)
        self.fig.update_layout(title={'text': "JV Curve",
                                      'x': 0.5,
                                      'y': 0.95,
                                      'xanchor': 'center',
                                      'yanchor': 'top'},
                               xaxis=dict(range=[-0.2, 0.8],
                                          showgrid=True,
                                          zeroline=True,
                                          zerolinewidth=2,
                                          zerolinecolor='#4b2e83',
                                          title='Voltage [V]',
                                          linecolor='#4b2e83',
                                          linewidth=2,
                                          gridwidth=1,
                                          gridcolor='#b7a57a'),
                               yaxis=dict(range=[-5, 20],
                                          showgrid=True,
                                          zeroline=True,
                                          zerolinewidth=2,
                                          zerolinecolor='#4b2e83',
                                          title='Current Density [mA/cm^2]',
                                          linecolor='#4b2e83',
                                          linewidth=2,
                                          gridwidth=1,
                                          gridcolor='#b7a57a'),
                               font=dict(family='Rockwell',
                                         size=18,
                                         color='#4b2e83'),
                               paper_bgcolor='gainsboro',
                               plot_bgcolor='#ffffff')

        # Added a checkbox for future including/excluding from calculation
        # self.checkbox = wx.CheckBox(self, label='Check Box')
        # self.Bind(wx.EVT_CHECKBOX, self.onChecked)
        # self.sizer.Add(self.checkbox, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        # Added a button for excluding the plot from average:
        self.zbutton = wx.Button(self, -1, "Zoom-in")
        self.zbutton.Bind(wx.EVT_BUTTON, self.OnZoom)
        self.hsizer.Add(self.zbutton, 0, wx.LEFT, 5)

        # Added a toggle button for including/excluding the plot from average:
        self.button = wx.ToggleButton(self, -1, "Exclude from average")
        self.button.Bind(wx.EVT_TOGGLEBUTTON, self.OnClicked)
        self.hsizer.Add(self.button, 0, wx.LEFT, 5)

        self.sizer.Add(self.hsizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        # Finishing the sizer setup:
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()

    # Defined a button
    def OnClicked(self, event):
        global flags
        if flags[self.num] == 1:
            flags[self.num] = 0
            event.GetEventObject().SetLabel("Include in average")
        else:
            flags[self.num] = 1
            event.GetEventObject().SetLabel("Exclude from average")

    # Defined a checkbox
    # def onChecked(self, event):
        # checkbox = event.GetEventObject()
        # print(checkbox.GetLabel(), ' is clicked', checkbox.GetValue())

    def OnZoom(self, event):
        self.win = PlotlyViewer(self.fig)


# Class that makes the plotly zoom-in chart to appear:
class PlotlyViewer(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, fig, exec=True):
        # Create a QApplication instance or use the existing one if it exists
        self.app = QApplication.instance() if QApplication.instance() \
                   else QApplication(sys.argv)

        super().__init__()

        self.file_path = os.path.abspath(os.path.join(os.path.dirname(
                                                      __file__), "temp.html"))
        plotly.offline.plot(fig, filename=self.file_path, auto_open=False)
        self.load(QUrl.fromLocalFile(self.file_path))
        self.setWindowTitle("Zoom-in")
        self.show()

        if exec:
            self.app.exec_()

    def closeEvent(self, event):
        os.remove(self.file_path)


# Created a scrollable panel of 8 panels:
class ScrolledPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, id=wx.ID_ANY, style=wx.BORDER_SUNKEN):
        scrolled.ScrolledPanel.__init__(self, parent=parent, style=style,
                                        size=(400, 400))

        # Define data for each one of 8 windows:
        self.plots = [0, 0, 0, 0, 0, 0, 0, 0]
        self.vals = [0, 0, 0, 0, 0, 0, 0, 0, [0, 0, 0, 0]]
        self.number = [0, 1, 2, 3, 4, 5, 6, 7]

        # self.list_ctrl = wx.ListCtrl(self,
        #                              style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        # self.list_ctrl.InsertColumn(0, 'Filename')

        self.plots = self.onOpenDirectory()
        self.vals = self.calcVals(self.plots)

        # Add button to the top panel:
        # btn = wx.Button(self, label="Export Values")
        # btn.Bind(wx.EVT_BUTTON, self.onClick)

        # Define 8 split windows:
        self.sp = wx.SplitterWindow(self)
        panel1 = panel(self.sp, self.plots[0], self.vals[0], self.number[0])
        panel2 = panel(self.sp, self.plots[1], self.vals[1], self.number[1])
        self.sp.SplitVertically(panel1, panel2)
        self.sp2 = wx.SplitterWindow(self)
        panel3 = panel(self.sp2, self.plots[2], self.vals[2], self.number[2])
        panel4 = panel(self.sp2, self.plots[3], self.vals[3], self.number[3])
        self.sp2.SplitVertically(panel3, panel4)
        self.sp3 = wx.SplitterWindow(self)
        panel5 = panel(self.sp3, self.plots[4], self.vals[4], self.number[4])
        panel6 = panel(self.sp3, self.plots[5], self.vals[5], self.number[5])
        self.sp3.SplitVertically(panel5, panel6)
        self.sp4 = wx.SplitterWindow(self)
        panel7 = panel(self.sp4, self.plots[6], self.vals[6], self.number[6])
        panel8 = panel(self.sp4, self.plots[7], self.vals[7], self.number[7])
        self.sp4.SplitVertically(panel7, panel8)

        # Define sizer:
        sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 0)
        # sizer.Add(btn, 0, wx.ALL | wx.CENTER, 0)

        sizer.Add(self.sp, 1, wx.EXPAND)
        sizer.Add(self.sp2, 1, wx.EXPAND)
        sizer.Add(self.sp3, 1, wx.EXPAND)
        sizer.Add(self.sp4, 1, wx.EXPAND)

        self.SetupScrolling()
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    # Function to open files:
    def onOpenDirectory(self):
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            self.folder_path = dlg.GetPath()
            ScrolledPanel.updateDisplay(self, self.folder_path)
        dlg.Destroy()
        return self.plots

    # Function to calculated values from raw data:
    def calcVals(self, plots):
        for i in range(0, 8):
            JVinterp = interp1d(self.plots[i][:, 0], self.plots[i][:, 2],
                                kind='cubic', bounds_error=False,
                                fill_value='extrapolate')
            JscL = -JVinterp(0)
            VocL = fsolve(JVinterp, .95 * max(self.plots[i][:, 0]))
            PPV = fmin(lambda x: x * JVinterp(x), .8 * VocL, disp=False)
            PCE = -PPV * JVinterp(PPV)
            FF = PCE / (JscL * VocL) * 100
            self.vals[i] = [PCE.item(), VocL.item(), JscL.item(), FF.item()]
            # self.vals[8] = [self.vals[8][0] + .125 * PCE.item(),
            #                 self.vals[8][1] + .125 * VocL.item(),
            #                 self.vals[8][2] + .125 * JscL.item(),
            #                 self.vals[8][3] + .125 * FF.item()]
        return self.vals

    # Function to update file names (?):
    def updateDisplay(self, folder_path):
        paths = glob.glob(self.folder_path + "/*.liv1")
        for i in range(0, 8):
            self.plots[i] = pd.read_csv(paths[i], delimiter='\t', header=None)
            idx_end = self.plots[i][self.plots[i].iloc[:, 0] ==
                                    'Jsc:'].index[0]
            self.plots[i] = self.plots[i].iloc[:idx_end - 1, :]
            self.plots[i].iloc[:, 0] = pd.to_numeric(self.plots[i].iloc[:, 0])
            self.plots[i] = np.array(self.plots[i])
            self.plots[i] = np.insert(self.plots[i], 2, -self.plots[i][:, 1],
                                      axis=1)

            # self.plots[i] = np.loadtxt(paths[i], delimiter='\t',
            #                            max_rows=34)
            # self.plots[i] = self.plots[i] * -1
        # for index, pth in enumerate(paths):
        #     self.list_ctrl.InsertItem(index, os.path.basename(pth))
        return self.folder_path

    # Function to output calculated data summary as csv file:
    def onClick(self, vals):
        filename = "output.csv"
        global flags
        print(flags)
        # Calculating the average of only "included" plots
        # Way # 1: using the "numpy dot product" finction to find a dot product
        # between a given column and flag values (either 0 or 1):
        self.vals[8][0] = np.dot([item[0] for item in self.vals][0:8],
                                 flags)/sum(flags)
        self.vals[8][1] = np.dot([item[1] for item in self.vals][0:8],
                                 flags)/sum(flags)
        self.vals[8][2] = np.dot([item[2] for item in self.vals][0:8],
                                 flags)/sum(flags)
        self.vals[8][3] = np.dot([item[3] for item in self.vals][0:8],
                                 flags)/sum(flags)

        # Way # 2:
        # First creating zero values for the average. Without this step after
        # each click and un-click of the "include/exlude" button and export,
        # the new everage will incorporate not only charts with flag=1,
        # but also the previous average value:
        """
        self.vals[8][0] = 0
        self.vals[8][1] = 0
        self.vals[8][2] = 0
        self.vals[8][3] = 0

        for i in range(0, 8):
            if flags[i] == 1:
                self.vals[8][0] += self.vals[i][0]
                self.vals[8][1] += self.vals[i][1]
                self.vals[8][2] += self.vals[i][2]
                self.vals[8][3] += self.vals[i][3]
        self.vals[8][0] /= sum(flags)
        self.vals[8][1] /= sum(flags)
        self.vals[8][2] /= sum(flags)
        self.vals[8][3] /= sum(flags)
        """

        # In order to add a column of device index including the 'average' I am
        # converting the data type to string and self.vals to array:
        self.vals = np.array(self.vals)
        self.vals = np.array(self.vals)
        if self.vals.shape[1] == 4:
            self.vals = np.append(self.vals,
                                  [[1], [2], [3], [4], [5], [6],
                                   [7], [8], [0]],
                                   axis=1)
        else:
            pass

        # if sum(flags) != 8:
        #     self.vals[8][0] *= 8
        #     self.vals[8][1] *= 8
        #     self.vals[8][2] *= 8
        #     self.vals[8][3] *= 8
        #     for i in range(0, 8):
        #         if flags[i] == 0:
        #             self.vals[8][0] -= self.vals[i][0]
        #             self.vals[8][1] -= self.vals[i][1]
        #             self.vals[8][2] -= self.vals[i][2]
        #             self.vals[8][3] -= self.vals[i][3]
        #     self.vals[8][0] /= sum(flags)
        #     self.vals[8][1] /= sum(flags)
        #     self.vals[8][2] /= sum(flags)
        #     self.vals[8][3] /= sum(flags)
        output = pd.DataFrame(self.vals,
                              columns=['PCE', 'Voc', 'Jsc', 'FF', 'Device'],
                              dtype=str)
        output['Device'].iloc[8] = 'Average'
        output.to_csv(filename)
        # np.savetxt(filename, output, delimiter=",", fmt='%s',
        #            header='PCE, Voc, Jsc, FF, Device')


# Genetal class for a pop-up window:
class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600, 400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())


# A class for a "about" message box:
class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About OPV Analysis UI",
                           style=wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER |
                           wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400, 200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        # btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()


# New class, not in use yet, supposed to hold a list of filenames
# Not finished:
class FileNameBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "File Names",
                           style=wx.DEFAULT_DIALOG_STYLE |
                           wx.RESIZE_BORDER |
                           wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400, 400))
        hwin.SetPage("File Names will be here")
        # btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()


# Main Frame now only has a scrolled panel
class Main(wx.Frame):
    def __init__(self):
        # Retrieving the screen size so that our window is on full screen
        # Later I want to find a way how to make it Global variables:
        screenSize = wx.DisplaySize()
        # screenWidth = screenSize[0]
        # screenHeight = screenSize[1]

        wx.Frame.__init__(self, parent=None, title="JV Curves",
                          size=screenSize,
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)

        self.SetBackgroundColour("#4b2e83")

        # Define main sizer for the main frame:
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Define Menu bar:
        menuBar = wx.MenuBar()

        # Add "File" tab to the manu bar:
        menu = wx.Menu()
        menuBar.Append(menu, "&File")

        # Add "Quit" option to the File tab:
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X",
                             "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)

        # Add "Help" tab to the manu bar:
        menu = wx.Menu()
        menuBar.Append(menu, "&Help")  # Add "help" tab to the manu bar

        # Add "About" tab to the manu bar:
        menu = wx.Menu()
        menuBar.Append(menu, "&About")  # Add "about" tab to the manu bar

        # Add "About" window option to the About tab:
        m_about = menu.Append(wx.ID_ABOUT, "&About",
                              "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)

        # Finalize Menubar setup:
        self.SetMenuBar(menuBar)
        self.statusbar = self.CreateStatusBar()

        # Define a sizer for the top panel that will have different buttons:
        topsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Define "Welcome message" text:
        m_text = wx.StaticText(self, -1, "This can be a welcome message")
        m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        m_text.SetSize(m_text.GetBestSize())
        m_text.SetForegroundColour('#ffffff')
        sizer.Add(m_text, 0, wx.ALL, 5)

        # Define a button for files names:
        m_files = wx.Button(self, label="Files")
        m_files.Bind(wx.EVT_BUTTON, self.OnFiles)
        topsizer.Add(m_files, 0, wx.ALL, 5)

        # Define scroll bar for the Main Frame:
        scroll = ScrolledPanel(self)

        # Add button to the top panel:
        m_export = wx.Button(self, label="Export Values")
        m_export.Bind(wx.EVT_BUTTON, scroll.onClick)
        topsizer.Add(m_export, 0, wx.ALL, 5)

        # Define "Exit" button:
        m_close = wx.Button(self, wx.ID_CLOSE, "Exit")
        m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        topsizer.Add(m_close, 0, wx.ALL, 5)

        # Add top panel with  buttons to the main sizer:
        sizer.Add(topsizer, 0, wx.ALL, 5)

        # Add Scrolled Panel to the main sizer:
        sizer.Add(scroll, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    # Function that closes a window:
    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               "Do you really want to close this application?",
                               "Confirm Exit", wx.OK | wx.CANCEL |
                               wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    # Function for "About" option in Menu:
    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    # Function for "Files" option in Menu:
    def OnFiles(self, event):
        dlg = FileNameBox()
        dlg.ShowModal()
        dlg.Destroy()


app = wx.App(redirect=False)
frame = Main()
frame.Show()
app.MainLoop()