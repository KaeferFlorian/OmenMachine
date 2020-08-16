# coding: utf-8

""" This is an example on how to run a GUI version of the card recommendation system.
"""

import os
import sys
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
import urllib.parse
from PIL import Image, ImageTk
import io
import webbrowser
sys.path.append('../')

import omenmachine
from run_example import prepOM
sys.path.append('./gui')
from autocomplete import Combobox_Autocomplete

class OMgui(tk.Tk):
    ''' Class that allows to switch between frames '''
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None

        # Prepare ML class
        self.om = prepOM()

        # General settings
        self.pady = 5
        self.padx = 1
        self.width = 5

        # create frame for title
        self.TopPage = TopPage(self)
        self.TopPage.pack()

        self.switchFrame(QueryPage)


    def switchFrame(self, frameClass):
        newFrame = frameClass(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = newFrame
        self._frame.pack()


class TopPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Define the grid
        #for ii in range(3):
        #    self.columnconfigure(ii, weight=1)

        # Get logo
        scaleFactor = 0.2
        size = (np.int(342*scaleFactor), np.int(288*scaleFactor))
        img = Image.open('gui/OmenMachineLogo.png')
        img = img.resize(size, Image.ANTIALIAS)
        logoImg = ImageTk.PhotoImage(img)

        logo = tk.Label(self, image=logoImg)
        logo.image = logoImg
        # sticky=tk.W+tk.E: for automatic adjustment when changing window size
        logo.grid(row=0, column=0, sticky=tk.W+tk.E, columnspan=1)

        # Create title
        title = tk.Label(self, text='Omen Machine')
        title.config(font=('Helvetica', 40, 'bold'))
        title.grid(row=0, column=2, sticky=tk.W+tk.E, columnspan=6)


class QueryPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Define the grid
        #for ii in range(14):
        #    self.columnconfigure(ii, weight=1)
        
        row=0

        # Create Card Name selection
        cardLabel = tk.Label(self, anchor="w", text='Magic Card Name:')
        cardLabel.grid(row=row, column=0, sticky=tk.W+tk.E)
        
        self.cardName = Combobox_Autocomplete(self, master.om.uniqueNames, highlightthickness=1)
        self.cardName.grid(row=row, column=1, sticky=tk.W+tk.E, columnspan=3)
        row+=1

        # Create Entry for CMC selection
        cmcLabel = tk.Label(self, anchor="w", text='CMC:')
        cmcLabel.grid(row=row, column=0, sticky=tk.W+tk.E)
        
        cmcOptions=[
            ">=",
            ">",
            "<=",
            "<",
            "==",
            "!="
            ]

        self.cmcBox = self.createBoxEntry(
            values=cmcOptions,
            row=row, column=1,
            entryColSpan=1
            )

        self.cmcEntry = self.createLabelEntry('0', row, column=2, entryWidth=master.width)

        row+=1

        # Create Checkbuttons to select colors
        colLabel = tk.Label(self, anchor="w", text='Colors:')
        colLabel.grid(row=row, column=0, sticky=tk.W+tk.E)

        self.colors = ['W', 'U', 'B', 'R', 'G', 'C']
        self.colorsLabel = ['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless']
        
        self.colEntries = []
        for ii,(rr,ll) in enumerate(zip(self.colors,self.colorsLabel)):
            self.colEntries.append(self.createCheckButtonEntry(rr, row, ii+1, ll))

        row+=1

        # Create Checkbuttons to select commander colors
        comLabel = tk.Label(self, anchor="w", text='Commander:')
        comLabel.grid(row=row, column=0, sticky=tk.W+tk.E)

        self.comEntries = []
        for ii,(rr,ll) in enumerate(zip(self.colors,self.colorsLabel)):
            self.comEntries.append(self.createCheckButtonEntry(rr, row, ii+1, ll))

        row+=1

        # Create Checkbuttons to select rarity
        rarLabel = tk.Label(self, anchor="w", text='Rarity:')
        rarLabel.grid(row=row, column=0, sticky=tk.W+tk.E)

        self.rarities = ['common', 'uncommon', 'rare', 'mythic']
        
        self.rarEntries = []
        for ii,rr in enumerate(self.rarities):
            self.rarEntries.append(self.createCheckButtonEntry(rr, row, ii+1, 'upperCase'))

        row+=1
        
        # Create Box to select legality
        formatLabel = tk.Label(self, anchor="w", text='Format:')
        formatLabel.grid(row=row, column=0, sticky=tk.W+tk.E)

        formatsValues=[
            "",
            "Standard",
            "Future Standard",
            "Historic",
            "Pioneer",
            "Modern",
            "Legacy",
            "Pauper",
            "Vintage",
            "Penny Dreadful",
            "Commander",
            "Brawl",
            "Duel Commander",
            "Old School 93/94",
            ]

        self.formatsBox = self.createBoxEntry(
            values=formatsValues,
            row=row, column=1,
            entryColSpan=1
            )

        row+=1

        
        # Create Checkbuttons to select rarity
        typeLabel = tk.Label(self, anchor="w", text='Types:')
        typeLabel.grid(row=row, column=0, sticky=tk.W+tk.E)

        self.types = [
            'Artifact', 'Conspiracy', 'Creature', 'Emblem',
            'Enchantment', 'Hero', 'Instant', 'Land',
            'Phenomenon', 'Plane ', 'Planeswalker', 'Scheme',
            'Sorcery', 'Tribal', 'Vanguard'
            ]

        self.typEntries = []
        ii=1
        for rr in self.types:
            if ii != 0 and ii % 7 == 0: # do a line break every 6 columns
                row+=1
                ii=1

            self.typEntries.append(self.createCheckButtonEntry(rr, row, ii))
            ii+=1

        row+=1

        # Create entry to select query number
        queryLabel = tk.Label(self, anchor="w", text='Query Number:')
        queryLabel.grid(row=row, column=0, sticky=tk.W+tk.E)
        
        self.queryEntry = self.createLabelEntry('9', row, column=1, entryWidth=master.width)

        row+=1

        # Button to exit window
        exitButton = tk.Button(self, text='Quit', width=master.width, command=master.destroy)
        exitButton.grid(row=row, column=0, sticky=tk.W+tk.E)

        # Button to reset querry
        resetButton = tk.Button(self, text='Reset', width=master.width, command=lambda: master.switchFrame(QueryPage))
        resetButton.grid(row=row, column=1, sticky=tk.W+tk.E)

        # Button to submit job
        def onSubmitButton():
            if self.cardName.get() == "":
                master.magicCard = "Omen Machine"
            else:
                master.magicCard = self.cardName.get()
            
            # CMC filter
            cmcNumber = self.cmcEntry.get()
            # Check if it is an integer
            try:
                cmcNumber = str(int(cmcNumber))
            except ValueError:
                cmcNumber='0'

            cmcOpt = self.cmcBox.get()
            master.cmcFilter = cmcOpt+cmcNumber

            # Color filter
            master.colorFilter = [col.get() for col in self.colEntries if col.get()] # if col.get() removes empty strings
            if master.colorFilter == self.colors:
                master.colorFilter = None

            # Commander filter
            master.commanderFilter = [com.get() for com in self.comEntries if com.get()]

            # Rarity filter
            master.rarityFilter = [rar.get() for rar in self.rarEntries if rar.get()]

            # Type filter
            master.typeFilter = [typ.get() for typ in self.typEntries if typ.get()]

            # Query number
            master.queryNumber = self.queryEntry.get()
            
            # Check if it is an integer
            try:
                master.queryNumber = int(master.queryNumber)
            except ValueError:
                master.queryNumber=9
           
            # Format filter
            if self.formatsBox.get() == "":
                master.legalityFilter = None
            else:
                master.legalityFilter = self.formatsBox.get().lower()

            master.switchFrame(ResultPage)


        submitButton = tk.Button(self, text='Submit', width=master.width, command=onSubmitButton)
        submitButton.grid(row=row, column=2, sticky=tk.W+tk.E)



    def createBoxEntry(self, values, row, column, entryColSpan):
        def changeBoxValue():
            box["values"] = values

        box = ttk.Combobox(self, values=values, postcommand=changeBoxValue)
        box.grid(row=row, column=column, sticky=tk.W+tk.E, columnspan=entryColSpan)
        box.current(0)

        return box


    def createCheckButtonEntry(self, text, row, column, label='sameAsText'):
        if label=='sameAsText':
            label=text
        elif label=='upperCase':
            label=text.title()

        checkVar = tk.StringVar()
        cc = tk.Checkbutton(
            self, text=label, variable=checkVar,
            onvalue=text, offvalue='',# height=5, width=20
            )

        checkVar.set(text) # set to being selected by default

        cc.grid(row=row, column=column, sticky=tk.W+tk.E)

        return checkVar


    def createLabelEntry(self, eText, row, column, entryWidth):
        def onEntryClick(event):
            """ this function gets called whenever text is clicked """
            if entry.get() == eText:
               entry.delete(0, "end") # delete text in entry
               entry.insert(0, '') # insert blank   

        def onFocusOut(event):
            if entry.get() == '':
                entry.insert(0, eText)

        entry = tk.Entry(self, width=entryWidth)
        entry.insert(0, eText)
        entry.bind('<FocusIn>', onEntryClick)
        entry.bind('<FocusOut>', onFocusOut)

        entry.grid(row=row, column=column, sticky=tk.W+tk.E, columnspan=1)

        return entry






class ResultPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        row=0

        df = master.om.getSimilarCards(
            master.magicCard,
            master.cmcFilter,
            master.colorFilter,
            master.commanderFilter,
            master.typeFilter,
            master.rarityFilter,
            master.legalityFilter,
            master.queryNumber
            )

        # Get images
        row=0

        ii=0
        images = []
        '''
        for index, (name, scryUrl, imgUrl, simScore) in enumerate(zip(
            df['name'].values,
            df['scryfall_uri'].values,
            df['image_uris.large'].values,
            df['sim_value'].values
            )):
        '''
        for index, rowDf in df.iterrows():
            imgUrl = rowDf['image_uris.large']

            if imgUrl != imgUrl:
                # Check if imgUrl is nan
                # Then URL is stored in cardfaces
                imgUrl = rowDf['card_faces'][0]['image_uris']['large']

            if ii != 0 and ii % 5 == 0: # do a line break every 5 columns
                row+=1
                ii=0

            image = self.createImgOutput(
                rowDf['name'],
                rowDf['scryfall_uri'],
                imgUrl,
                rowDf['sim_value'],
                row, ii)

            # Keep the reference by appending to list
            images.append(image)

            ii+=1

            '''
            rawImg = urllib.request.urlopen(imgUrl).read()
            img = Image.open(io.BytesIO(rawImg))

            scaleFactor = .3
            #w, h = img.size
            # For a normal card it will be (672, 936)
            # Speial Cards, e.g. a "Plane" will be forced to match this size
            w, h = 672, 936
            size = (np.int(w*scaleFactor), np.int(h*scaleFactor))
            img = img.resize(size, Image.ANTIALIAS)

            image = ImageTk.PhotoImage(img)
            imgLabel = tk.Label(self, image=image, text="{0}: {1:.2f}".format(name, simScore), compound=tk.BOTTOM)
            imgLabel.image = image
            if ii != 0 and ii % 5 == 0: # do a line break every 5 columns
                row+=1
                ii=0
            
            imgLabel.grid(row=row, column=ii, sticky=tk.W+tk.E, columnspan=1, pady=15)

            # Bind click event to image
            imgLabel.bind('<Button-1>', lambda event, scryUrl=scryUrl: onImgClick(event, scryUrl))

            # Keep the reference by appending to list
            images.append(image)
            
            ii+=1
            '''


        row+=1

        # Button to exit window
        exitButton = tk.Button(self, text='Quit', width=master.width, command=master.destroy)
        exitButton.grid(row=row, column=0, sticky=tk.W+tk.E)

        # Button to reset querry
        resetButton = tk.Button(self, text='Reset', width=master.width, command=lambda: master.switchFrame(QueryPage))
        resetButton.grid(row=row, column=1, sticky=tk.W+tk.E)


    def createImgOutput(self, name, scryUrl, imgUrl, simScore, row, column):
        
        def onImgClick(event, scrUrl):
            webbrowser.open(scryUrl, new=0) # new=2 opens it in new tab

        rawImg = urllib.request.urlopen(imgUrl).read()
        img = Image.open(io.BytesIO(rawImg))

        scaleFactor = .3
        #w, h = img.size
        # For a normal card it will be (672, 936)
        # Speial Cards, e.g. a "Plane" will be forced to match this size
        w, h = 672, 936
        size = (np.int(w*scaleFactor), np.int(h*scaleFactor))
        img = img.resize(size, Image.ANTIALIAS)

        image = ImageTk.PhotoImage(img)
        imgLabel = tk.Label(self, image=image, text="{0}: {1:.2f}".format(name, simScore), compound=tk.BOTTOM)
        imgLabel.image = image
            
        imgLabel.grid(row=row, column=column, sticky=tk.W+tk.E, columnspan=1)

        # Bind click event to image
        imgLabel.bind('<Button-1>', lambda event, scryUrl=scryUrl: onImgClick(event, scryUrl))

        return image

if __name__ == '__main__':
    gui = OMgui()
    
    # Add title to window
    gui.title('Omen Machine')

    # Define default geometry of the window
    gui.minsize(1040,720)

    gui.mainloop()
