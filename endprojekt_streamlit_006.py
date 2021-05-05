""" Projektarbeit Gruppe X: Helena Brinkmann, Eugen Sperling und Daniel Andrade
Ziel der Arbeit: Inwieweit beeinflusst das Bevölkerungswachstum/-entwicklung den Außenhandel
bzw. Export eines Landes. """

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
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
import streamlit as st


def main():
    my_data_path = "daten/"
    
    filehandler = data_handler()     # Initialize a data_handler object for later reading and handling of the data
    
    # # Read the data and save as a PandaFrame
    df_pop = filehandler.read_data(my_data_path + "pop_FAOSTAT_data_5-4-2021.csv")
    df_export = filehandler.read_data(my_data_path + "export_value_base_FAOSTAT_data_5-4-2021.csv")
    df_prod = filehandler.read_data(my_data_path + "production_FAOSTAT_data_5-5-2021.csv")

    # # Rename the columns: Instead of 'Values', the name of the column is changed 
    df_export = filehandler.rename_column(df_export, "EVBP")
    df_pop = filehandler.rename_column(df_pop, "Pop")
    df_prod = filehandler.rename_column(df_prod, "Production")

    # # Safe work files as Json-File:
    filehandler.save_data(df_pop)
    filehandler.save_data(df_prod)
    filehandler.save_data(df_export)

    ## # Now we only want to use some of the data - Strip data to relevant parts:
    df_clean_data = filehandler.general_data(df_export, df_pop, df_prod)
    filehandler.save_data(df_clean_data)    # Saving of the new Dataframe


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
    # countries = ["Germany"]
    ana = analysis()
    # print("\n analysis: \n")
    # print(ana.ols_regression(df_clean_data))

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

    #test in local with:    streamlit run endprojekt_streamlit_006.py

    st.write("**Abhängigkeit des Exports bzw. der Produktion von der Bevölkerungsentwicklung**", type="multiline")
    #print("**_Abhängigkeit des Exports bzw. der Produktion von der Bevölkerungsentwicklung_**")
    st.write("FAO analyzer v1.1")

    #-------------------------------------description:
    description =("_Fragestellung: In wieweit beeinflusst die Bevölkerungsentwicklung das Export bzw. die Produktion von Lebensmittel? Am Beispiel von drei Länder._")
    st.write(description)
    st.write("Data Description:")
    st.dataframe(df_clean_data.describe())

    #-----------------------------------------quick glance plot:
    st.write("Comparision of all the countries together:")
    fig1 = plothandler.simple_plot(df_clean_data)
    st.pyplot(fig1)

    #----------------------------auswahl daten:

    #clean up data/ sanitize part:

    #auswahl für länder?

    my_label = st.selectbox("Please select one country", ["Brazil","Cambodia", "Germany"])
    countries = [my_label]
    # countries.append(my_label)

    #------------------------analysis
    information = "_Now you can analyse the choosen country:_"
    st.write(information)

    #thesis/ Fragestellung hier??

    #regression?? / methoden?

    
    st.pyplot(ana.ols_regression(df_clean_data, my_label), type="multiline")
    


    #-------------------------better plots

    #schoene plots um endergebnis darzustellen???
    fig3 = plothandler.relative_data_plot(countries, df_export, df_pop, "EVBP", "Pop")
    st.pyplot(fig3)
    fig4 = plothandler.relative_data_plot(countries, df_prod, df_pop, "Production", "Pop")
    st.pyplot(fig4)


    for i in countries:
        fig5 = sns.jointplot(x="Pop", y="EVBP", data=df_clean_data[df_clean_data['Area']==i], kind = 'reg',fit_reg= True, size = 7)
        st.pyplot(fig5)
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
        dataframe.to_json(f'daten/{filename}.json')
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

        fig1, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
        fig1.suptitle("Comparision of population growth and export value base price / production")
        plt1 = sns.lineplot(ax=ax1, x="Year", y="Pop", hue="Area", data=dataframe)
        plt1.set_yscale("log")
        plt2 = sns.lineplot(ax=ax2, x="Year", y="EVBP", hue="Area", data=dataframe)
        plt2.set_yscale("log")
        plt2 = sns.lineplot(ax=ax3, x="Year", y="Production", hue="Area", data=dataframe)
        plt2.set_yscale("log")
        # plt.show()

        #fig, ax = plt.subplots() #solved by add this line 
        #ax = sns.lineplot(data=pd.DataFrame(data), x="Demand", y="price")
        return fig1

    def relative_data_plot(self, countrieslist, dataframe1, dataframe2, keynamedata1, keynamedata2):
        countries_dep, countries_pop = [], []
        for i in countrieslist:
            countries_dep = self.filehandler.relative_columnvalue(dataframe1, i, keynamedata1, countries_dep)
            countries_pop = self.filehandler.relative_columnvalue(dataframe2, i, keynamedata2, countries_pop)

        for i in range(len(countrieslist)):
            plt.scatter(countries_pop[i], countries_dep[i])

        plt.xlabel(f"{keynamedata2} - Increament Factor")
        plt.ylabel(f"{keynamedata1} - Increament Factor") # NOCH GEÄNDERT
        # plt.show()


class analysis():
    #lin regression/ plynom/ exp??

    def ols_regression(self, dataframe, mylabel):
        m = ols('EVBP ~ Pop', dataframe[dataframe["Area"] == mylabel]).fit()
        fig2 = plt.text(0.01, 0.05, str(m.summary()), {'fontsize': 10}, fontproperties = 'monospace')
        # plt.axis("off")
        # plt.tight_layout()
        fig2 = plt.savefig("ols.png")
        return fig2


if __name__ == "__main__":
    main()
