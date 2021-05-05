""" Projektarbeit Gruppe X: Helena Brinkmann, Eugen Sperling und Daniel Andrade
Ziel der Arbeit: Inwieweit beeinflusst das Bevölkerungswachstum/-entwicklung den Außenhandel
bzw. Export eines Landes. 
Tabellen, die vom Internet gezogen sind: """

"""[summary]

Returns:
    [type]: [description]

TODO: * change file locations/ relative path??
        * change file save name
        * use with open in file handler class
        * use decorator @st.cache ??
        * mongo db integrieren??
        * clean up
        * remove plt.show()
"""
#imports:

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
import streamlit as st


def main():
    #main loop to run:
    
    #initialize a data_handler object:
    filehandler = data_handler()
    #read in data:

    df_pop = filehandler.read_data("C:/Users/Eugen/OneDrive/Data_science/Big_data/python_big_data/Big_data_project/daten/pop_FAOSTAT_data_5-4-2021.csv")
    df_export = filehandler.read_data("C:/Users/Eugen/OneDrive/Data_science/Big_data/python_big_data/Big_data_project/daten/export_value_base_FAOSTAT_data_5-4-2021.csv")
    df_prod = filehandler.read_data("C:/Users/Eugen/OneDrive/Data_science/Big_data/python_big_data/Big_data_project/daten/production_FAOSTAT_data_5-5-2021.csv")

    #rename 
    df_export = filehandler.rename_column(df_export, "EVBP")
    df_pop = filehandler.rename_column(df_pop, "Pop")
    df_prod = filehandler.rename_column(df_prod, "Production")

    #safe work files:
    filehandler.save_data(df_pop)
    filehandler.save_data(df_prod)
    filehandler.save_data(df_export)

    #strip data to relevant parts:

    df_clean_data = filehandler.general_data(df_export, df_pop, df_prod)
    
    filehandler.save_data(df_clean_data)


    # # 1. Teil: Ist ein allgemeinen Trend in den Schaubildern da?

    #first look at the data:
    print("\nGeneral Data structure:\n",df_clean_data.info())

    print("\nGeneral Data cleaned:\n",df_clean_data.describe())

    
    #change print to streamlit

    plothandler = plotter_class()
    plothandler.simple_plot(df_clean_data)


    # print("Exports:\n", df_export.describe())
    # print("Population:\n", df_pop.describe())
    # print("Production:\n", df_prod.describe())

    # 

    #add simple plot ( no analysis)

    #analysis:

    ana = analysis()
    print("\n analysis: \n")
    print(ana.ols_regression(df_clean_data))

    # # 2. Teil: Hier werden die Trends genauer betrachtet und skaliert gesehen.
    
    countries = ["Brazil", "Cambodia", "Germany"]   #in streamlit als dropdown?? 
    
    #my_label = st.selectbox("Filter", ["age","gender", "split", "final"])
    
    #print description in streamlit what plot shows

    plothandler.relative_data_plot(countries, df_export, df_pop, "EVBP", "Pop")
    plothandler.relative_data_plot(countries, df_prod, df_pop, "Production", "Pop")


    for i in countries:
        sns.jointplot(x="Pop", y="EVBP", data=df_clean_data[df_clean_data['Area']==i], kind = 'reg',fit_reg= True, size = 7)
        plt.show()








    ## streamlit execution:
    #---------------------------------------------headline

    #test in local with:    streamlit run endprojekt_streamlit_004.py

    st.title("**_Abhängigkeit des Exports bzw. der Produktion von der Bevölkerungsentwicklung_**")
    #print("**_Abhängigkeit des Exports bzw. der Produktion von der Bevölkerungsentwicklung_**")
    st.write("FAO analyzer v1.0")


    #-------------------------------------description:

    description =("Fragestellung: tool um relation zwischen Bevoelkerungswachstum \
                    und expoerten ( lebensmittel?) zu iuntersuchen")

    st.write(description)

    #thesis/ Fragestellung hier??

    #----------------------------auswahl daten:

    #clean up data/ sanitize part:

    #auswahl für länder?

    my_label = st.selectbox("Filter", ["Area","Year"])

    #print out heads:

    st.write("Data information:")

    st.write("Data Description:\n", df_clean_data.describe())
    st.write("Data Info:\n", df_clean_data.info())

    # st.write("Population:\n", df_pop_new.describe())
    # st.write("Population:\n", df_pop_new.info())


    #-----------------------------------------quick glance plot:

    st.pyplot(plothandler.simple_plot(df_clean_data))


    #------------------------analysis

    st.write(description)

    #thesis/ Fragestellung hier??

    #regression?? / methoden?

    st.write(ana.ols_regression(df_clean_data))


    #-------------------------better plots

    #schoene plots um endergebnis darzustellen???

    st.pyplot(plothandler.relative_data_plot(countries, df_export, df_pop, "EVBP", "Pop"))
    st.pyplot(plothandler.relative_data_plot(countries, df_prod, df_pop, "Production", "Pop"))


    for i in countries:
        st.pyplot(sns.jointplot(x="Pop", y="EVBP", data=df_clean_data[df_clean_data['Area']==i], kind = 'reg',fit_reg= True, size = 7))
        #plt.show()


class data_handler():

    def read_data(self, filename):
        return pd.read_csv(filename)

    def rename_column(self, dataframe, column_key):
        dataframe = dataframe.rename(columns={"Value": column_key}) 
        return dataframe

    def save_data(self, dataframe):
        filename = ""
        for i in dataframe.columns:
            filename = filename + str(i) +"_"
        filename = filename.replace(" ","_")
        dataframe.to_json(f'C:/Users/Eugen/OneDrive/Data_science/Big_data/python_big_data/Big_data_project/saved_data/{filename}.json')
        print("file saved!")

        #mongo db wegspeichern ???
        #print outr con
        #df.to_json(r'Path to store the exported JSON file\File Name.json'

    def general_data(self, dataframe1, dataframe2, dataframe3):
        df_clean_data = dataframe1[["Area", "Year", "EVBP"]].copy()
        df_pop_new = dataframe2[["Pop"]].copy()
        df_prod_new = dataframe3[["Production"]].copy()
        df_clean_data = df_clean_data.join(df_pop_new)
        df_clean_data = df_clean_data.join(df_prod_new)
        return df_clean_data

    def relative_columnvalue(self, dataframe, country_name, column_key, liste):
        df = dataframe[["Area", "Year", column_key]].copy()
        df_red = df.pivot(index="Year", columns="Area", values=column_key)
        values = []
        for i in range(1961,2019):
            values.append(df_red[country_name][i]/df_red[country_name][1961])
        liste.append(values)
        return liste

class plotter_class():
    #simple plotter  class for plotting in streamlit
    def __init__(self):
        self.filehandler = data_handler()
    
    def simple_plot(self , dataframe):

        fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
        fig.suptitle("Comparision of population growth and export value base price")
        plt1 = sns.lineplot(ax=ax1, x="Year", y="Pop", hue="Area", data=dataframe)
        plt1.set_yscale("log")
        plt2 = sns.lineplot(ax=ax2, x="Year", y="EVBP", hue="Area", data=dataframe)
        plt2.set_yscale("log")
        plt2 = sns.lineplot(ax=ax3, x="Year", y="Production", hue="Area", data=dataframe)
        plt2.set_yscale("log")
        plt.show()

        #fig, ax = plt.subplots() #solved by add this line 
        #ax = sns.lineplot(data=pd.DataFrame(data), x="Demand", y="price")
        return fig

    def relative_data_plot(self, countrieslist, dataframe1, dataframe2, keynamedata1, keynamedata2):
        countries_dep, countries_pop = [], []
        for i in countrieslist:
            countries_dep = self.filehandler.relative_columnvalue(dataframe1, i, keynamedata1, countries_dep)
            countries_pop = self.filehandler.relative_columnvalue(dataframe2, i, keynamedata2, countries_pop)

        for i in range(len(countrieslist)):
            plt.scatter(countries_pop[i], countries_dep[i])

        plt.xlabel(f"{keynamedata2} - Increament Factor")
        plt.ylabel(f"{keynamedata1} - Increament Factor") # NOCH GEÄNDERT
        plt.show()


class analysis():
    #lin regression/ plynom/ exp??

    def ols_regression(self, dataframe):
        m = ols('EVBP ~ Pop',dataframe[dataframe["Area"] == "Brazil"]).fit()
        return m.summary()


if __name__ == "__main__":
    main()
