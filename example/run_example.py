# coding: utf-8

""" This is an example on how to run the card recommendation system.
"""

import os
import sys
sys.path.append('../')

import omenmachine


def main():
    # Define input / output files
    jsonFile = "default-cards-20200615170431.json"
    jsonUniqueFile='default-cards-unique.json'
    dfFile = "SimilarCardsDf"

    # Filter the original json file
    if not os.path.isfile(jsonUniqueFile):
        omenmachine.prepJsonFile(jsonFile, jsonUniqueFile, chatty=True)
    

    # Initialize class
    om = omenmachine.OmenMachine(jsonUniqueFile, dfFile, chatty=True)

    if not os.path.isfile(dfFile):
        om.runML()
    else:
        om.loadML()

    
    #magicCard = 'Alesha, Who Smiles at Death'
    magicCard = 'Omen Machine'
    sc = om.getSimilarCards(magicCard)


if __name__ == '__main__':
    main()
