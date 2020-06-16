# coding: utf-8

import re
import json
import joblib

import numpy as np
import pandas as pd
from pandas.io.json import json_normalize

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def prepJsonFile(jsonFile, jsonUniqueFile='default-cards-unique.json', chatty=True):
    # Load the json file downloaded from scryfall
    with open(jsonFile) as openFile:
        scryfallDefault = json.load(openFile)
        
    # The json file contains every card object on Scryfall.
    # Therefore, we need to filter out cards from different expansions that have the same name.
    # Get all unique card names:
    uniqueNames = []
    scryfall = []
    for card in scryfallDefault:
        if card['name'] not in uniqueNames:
            uniqueNames.append(card['name'])
            scryfall.append(card)
    
    with open(jsonUniqueFile, 'w') as outfile:
        json.dump(scryfall, outfile)

    if chatty:
        outPrint = 'Total number of cards in the Scryfall library: {0}'.format(len(scryfallDefault))
        outPrint += '\nUnique cards: {0}'.format(len(uniqueNames))
        print(outPrint)


class OmenMachine:
    """
    Class to build a content based recommendation system for Magic cards using scikit-learn.
    Given an existing card, the cosine similarity is used to find the most similar cards.
    Additional filters, for example color identity or legality in various formats can be applied.
    """
    
    def __init__(self, jsonUniqueFile, simDfFile, chatty=True):
        """
        :param jsonUniqueFile: Path to Scryfall's json file after filtering with the prepJsonFile function
        :param simDfFile: Data frame file where similarity information will be stored in/loaded from      
        
        Download options and more information can be found here:
        https://scryfall.com/docs/api/bulk-data
        
        In this example, we use the "Default Cards" json file, which contains every card object
        on Scryfall in English or the printed language if the card is only available in one language.
        """
        self.jsonUniqueFile = jsonUniqueFile
        self.simDfFile = simDfFile
        self.chatty = chatty
        
        # load the filtered json file
        self._loadFile()
    
    
    def _loadFile(self):
        # Load the json file downloaded from scryfall
        with open(self.jsonUniqueFile) as openFile:
            self.scryfall = json.load(openFile)
        
        self.uniqueNames = [card['name'] for card in self.scryfall]
        
        # Transform the json input to pandas dataframe. This flattens the dictionary
        # This causes Flip/Fuse cards etc. to have NaN values in e.g. the "colors" column
        # because it is stored in "card_faces"
        self.scryfallDf = json_normalize(self.scryfall)

    
    def _combineFeatures(self, card):
        """
        :param card: Data frame entry for an individual card on Scryfall
        """
        try:
            cardString = ''
            for feature in self.features:
                featureString = ''
                try:
                    featureString += str(card[feature])
                except KeyError:
                    # Cards with "Transform" need to be treated differently.
                    # Their oracle text is split for the different card_faces,
                    # e.g. "Delver of Secrets // Insectile Aberration" 
                    try:
                        for cf in (0,1):
                            featureString += card['card_faces'][cf][feature]+' '
                    except KeyError:  
                        # One ends up here when the card is for example an Instant
                        # and one checks for power/toughness keywords.
                        # Then, an empty string will be passed
                        # This choice depends on the posed problem
                        pass
                
                # Add feature string to card string
                cardString += featureString+' '
 
        except:
            if self.chatty:
                # Print the card properties in case there is an error
                print(card)
        
        # Remove possible description text in parenthesis.
        # For example: "Cycling—Sacrifice a land. (Sacrifice a land, Discard this card: Draw a card.)"
        # This will be reduced to: "Cycling—Sacrifice a land."
        cardString = re.sub(r" ?\([^)]+\)", "", cardString)
        # Remove additional irrelevant characters from
        # e.g. Fuse cards like "Wear // Tear"
        cardString = cardString.replace('//','').replace('—','')
        return ' '.join(cardString.split()) # Remove multiple white spaces
    
    
    def _prepML(self):
        """
        The relevant input for our machine-learning algorithm are the so-called features.
        These represent the card properties that we use to compare it to other cards.
        Example of interesting features are:
        - The oracle text, meaning a description of what the card does
        - The converted mana cost
        - The type of the card (e.g., Creature or Instant)
        ...
        """
        
        # Store the relevant features in a list
        self.features = ['cmc', 'mana_cost', 'type_line', 'oracle_text', 'power', 'toughness']
            
        # Combine the features in one string per card
        combinedFeatures = [self._combineFeatures(card) for card in self.scryfall]
        
        # Create a pandas dataframe 
        self.mlDf = pd.DataFrame(np.array([self.uniqueNames]).T)
        self.mlDf.columns = ['Names']
        self.mlDf['CombinedFeatures'] = combinedFeatures
        
        if self.chatty:
            self.mlDf.head()
        
    
    def runML(self):
        # Prepare features
        self._prepML()
        
        # Create count matrix from the combined feature column
        cv = CountVectorizer()
        countMatrix = cv.fit_transform(self.mlDf['CombinedFeatures'])

        # Compute the cosine similarity based on the count matrix
        cosineSim = cosine_similarity(countMatrix)
        
        # Store the similarity in dataframe
        self.similarCardsDf = pd.DataFrame(cosineSim, index=self.uniqueNames, columns=self.uniqueNames)
        
        if self.chatty:
            self.similarCardsDf
            
        # Dump it in a file
        joblib.dump(self.similarCardsDf, self.simDfFile)
    
    
    def loadML(self):
        # Load the pandas dataframe in which the similarity is stored as a correlation matrix
        self.similarCardsDf = joblib.load(self.simDfFile)

        
    def getSimilarCards(self, magicCard,
                        cmcFilter='>=0',
                        colorFilter = None,
                        commanderFilter = ['W', 'U', 'B', 'R', 'G', 'C'],
                        typeFilter = ['Artifact', 'Conspiracy', 'Creature', 'Emblem',
                                      'Enchantment', 'Hero', 'Instant', 'Land',
                                      'Phenomenon', 'Plane', 'Planeswalker', 'Scheme',
                                      'Sorcery', 'Tribal', 'Vanguard'],
                        rarityFilter = ['common', 'mythic', 'rare', 'uncommon'],
                        legalityFilter = None,
                        queryNumber=10):
    
        """ Function to return most similar cards
        
        :param magicCard: String of the card name to be queried
        :param cmcFilter: 
        :param colorFilter: 
        :param commanderFilter: 
        :param typeFilter: 
        :param rarityFilter: 
        :param legalityFilter:
        :param queryNumber: Defines how many card suggestions are returned
    
        Returns (list)
        """
        
        if magicCard not in self.uniqueNames:
            print('Magic card {0} is not in the database.'.format(magicCard))
            return -1

        similarityValues = self.similarCardsDf[magicCard].sort_values(ascending=False)    
        similarityValues = similarityValues.to_frame().reset_index()
        # Name the data frame columns to merge it
        similarityValues.columns = ['name', 'sim_value']
        
        # Merge the data frames
        similarityDf = pd.merge(similarityValues, self.scryfallDf, on='name')
        
        # Filter out the input Magic card
        maficCardDf = similarityDf[similarityDf.name == magicCard]
        similarityDf = similarityDf[similarityDf.name != magicCard]
        
        # Filter data frame according to "converted mana cost"
        similarityDf = similarityDf.query('cmc{0}'.format(cmcFilter))

        # Filter data frame according to card type
        similarityDf = similarityDf[
            [any(True if tf in tv else False for tf in typeFilter) for tv in similarityDf.type_line.values]
            ]
        
        # Filter data frame according to rarity
        similarityDf = similarityDf[
            [any(True if rf == rv else False for rf in rarityFilter) for rv in similarityDf.rarity.values]
            ]
                
        # Filter data frame according to containing all colors in "colorFilter"
        # e.g. [G,R] will show Gruul cards but for example also [W,G,R].
        if colorFilter is not None:     
            mask = []
            for index in range(len(similarityDf)):
                cv = similarityDf.iloc[index].colors
                if str(cv) == 'nan':
                    cv = similarityDf.iloc[index].card_faces[0]['colors']
                    if len(cv)==0:
                        cv = ['C']
                mask.append( all(True if cf in cv else False for cf in colorFilter) )
            similarityDf = similarityDf[mask]
        
        # Filter data frame according to commanders’ color identity
        allColors = np.array(['W', 'U', 'B', 'R', 'G', 'C'])
        antiCommanderFilter = allColors[ np.invert([any(cf in ac for cf in commanderFilter) for ac in allColors]) ]

        similarityDf = similarityDf[
            [all(False if ci in antiCommanderFilter else True for ci in cis) for cis in similarityDf.color_identity]
            ]
        
        # Filter data frame according to legality in different formats
        if legalityFilter is not None:
            similarityDf = similarityDf[
                [all(False if similarityDf['legalities.{0}'.format(lf)].iloc[index]=='not_legal' else True for lf in legalityFilter) for index in range(len(similarityDf))]
                ]
        
        similarityDf = similarityDf[:queryNumber]

        if self.chatty:
            # Define output parameters that will be printed
            outParams = ['name', 'sim_value', 'type_line', 'mana_cost', 'color_identity']
            print(maficCardDf[outParams])
            print('')
            print(similarityDf[outParams])

        return similarityDf
