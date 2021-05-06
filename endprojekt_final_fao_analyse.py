import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
import streamlit as st
from pymongo import MongoClient
import json

# # Init mongodb and connection to MongoDB
cluster = "mongodb+srv://alfabigdata:pw5478@cluster0mongotest.qtvn4.mongodb.net/FAO_analyzer?retryWrites=true&w=majority"
client = MongoClient(cluster)
db = client.FAO_analyzer
json_dump = db.json_dump     # Collection in der Datenbank FAO-Analyzer

def main():
    my_data_path = "daten/"     # Bitte jedes einzelne Benutzer anpassen! Lokaler Datenpfad für Ausführungen
    
    filehandler = data_handler()     # Initialize a data_handler object for later reading and handling of the data
    
    # # Read the data and save as a PandaFrame
    df_pop = filehandler.read_data(my_data_path + "pop_FAOSTAT_data_5-4-2021.csv")
    df_export = filehandler.read_data(my_data_path + "export_value_base_FAOSTAT_data_5-4-2021.csv")
    df_prod = filehandler.read_data(my_data_path + "production_FAOSTAT_data_5-5-2021.csv")

    # # Rename the columns: Instead of 'Values', the name of the column is changed (EVBP, Pop, Production)
    df_export = filehandler.rename_column(df_export, "EVBP")
    df_pop = filehandler.rename_column(df_pop, "Pop") 
    df_prod = filehandler.rename_column(df_prod, "Production")

    # # Save work files as Json-File:
    filehandler.save_data(df_pop)
    filehandler.save_data(df_prod)
    filehandler.save_data(df_export)

    # # Save to MongoDB:
    filehandler.dump_to_mongo(df_pop)
    filehandler.dump_to_mongo(df_prod)
    filehandler.dump_to_mongo(df_export)

    # # # Now we only want to use some of the data - Strip data to relevant parts:
    df_clean_data = filehandler.general_data(df_export, df_pop, df_prod)
    filehandler.save_data(df_clean_data)    # Saving of the new Dataframe
    filehandler.dump_to_mongo(df_clean_data)


    # # Initialize classes for plotting and analyzing
    plothandler = plotter_class()
    ana = analysis()

    ## Streamlit Execution:
    # # ---------- Headline

    # Test in local with (Terminal):    streamlit run endprojekt_final_fao_analyse.py
    st.write("Projektarbeit Gruppe E: Helena Brinkmann, Eugen Sperling und Daniel Andrade.")
    st.write("Big Data Analysis, Dozent: Thorsten Klein")
    st.write("Ziel der Arbeit: Inwieweit beeinflusst das Bevölkerungswachstum/-entwicklung den Außenhandel \
        bzw. Export eines Landes?", type = "multiline")
    st.header("**Abhängigkeit des Exports bzw. der Produktion der Agrarprodukte von der Bevölkerungsentwicklung**")
    st.write("")
    st.write("")
    st.write("FAO analyzer v1.3")

    # # ---------- Description:
    st.write("_Thesis: In wieweit beeinflusst die Bevölkerungsentwicklung das Export bzw. die Produktion von Agrarprodukte? Am Beispiel von drei Ländern, \
        ein Industrieland (Deutschland), ein Schwellenland (Brasilien) und ein Entwicklungsland (Kambodscha)._")
    st.write("Data Description:")
    st.dataframe(df_clean_data.describe())

    # # ---------- Quick glance plot:
    st.set_option('deprecation.showPyplotGlobalUse', False)     
    st.write("1. Schritt: Vergleich alle drei Ländern über die Jahren. Daten werden in einem einfachen Plot in einer \
        halblogarithmische Darstellung visualisiert")
    fig1 = plothandler.simple_plot(df_clean_data)    # Aufrufen der Klasse simple_plot
    st.pyplot(fig1)

    # # ---------- Auswahl der Daten:
    st.write("2. Schritt: Jedes Land wird einzel betrachtet. Erst wird das Export Value Base Price (Einheit: 1000 $), \
        anschließend die Prduktion (Gross Production Index Number) betrachtet.")
    st.write("_Hier wird einerseits die absolute Nummer betrachtet (zweites Schaubild), aber auch das Increment \
        Factor betrachtet, sodass die Daten um vergleichbare Skalen zu erhalten ('Normierung')._")
    my_label = st.selectbox("Wähle ein Land aus", ["Brazil","Germany", "Cambodia"])     # Hier Filtert man die Ergebnisse
    # # Nächster Schritt: Für alle Länder verallgemeinern.
    countries = [my_label]    # Speichern des gewählten Landes

    # # ---------- Analysis und Regression-Methoden

    # # Abhängigkeit von EVBP von der Population:
    st.write("**a) Abhängigkeit des Export Value Base Preis (Agricultural Products) von der Bevölkerungsentwicklung**")
    st.pyplot(ana.ols_regression("EVBP", df_clean_data, my_label))    # OLS Regression Results für das gewählte Land
    st.pyplot(plothandler.relative_data_plot(countries, df_export, df_pop, "EVBP", "Pop"))   # # Plotten der relativen Daten mit relative_data_plot
    # # Hier wird in diese Funktion eine andere Funktion aufgerufen (mit exponentielle Regression)
    st.pyplot(sns.jointplot(x="Pop", y="EVBP", data=df_clean_data[df_clean_data['Area']== my_label], kind = 'reg',fit_reg= True, size = 7))
    # # Erstellt eine lineare Regression mit den absoluten Daten

    # # Abhängigkeit von Produktion von der Population: Analog wie oben
    st.write("**b) Abhängigkeit des Produktion (Agricultural Products) von der Bevölkerungsentwicklung**")
    st.pyplot(ana.ols_regression("Production", df_clean_data, my_label))
    st.pyplot(plothandler.relative_data_plot(countries, df_prod, df_pop, "Production", "Pop"))
    st.pyplot(sns.jointplot(x="Pop", y="Production", data=df_clean_data[df_clean_data['Area']==countries[0]], kind = 'reg',fit_reg= True, size = 7))

    # # ---------- Schlussfolgerung
    st.write("**Schlussfolgerung** Hier kann man sehr gut zwischen die drei Arten Länder unterscheiden:")
    st.write("- In Brasilien, ein Schwellenland, sieht man einen eindeutigen exponentiellen Zusammenhang. Je größer die Bevölkerung, desto größer \
            die Produktion und der Export von Agrarprodukte.")
    st.write("- In Deutschland, ein Industrieland, ist der wirtschaftliche Wachtstum unabhängig von der Bevölkerungsentwicklung. Dieser wächst meist \
            kontinuierlich.")
    st.write("- In Kambodscha, ein Entwicklungsland, kann man unterschiedliches sehen. Während der Pol Pot-Diktatur gibt es kein wirtschaftlichen \
        Wachtstum, jedoch am Ende der Diktatur dieser und die Produktion stark zunehmen. ")
    
    st.write("**Appendix: Source-Code**")
    def code_text():
        return '''
        import numpy as np
        import pandas as pd
        import seaborn as sns
        import matplotlib.pyplot as plt
        from statsmodels.formula.api import ols
        import streamlit as st
        from pymongo import MongoClient
        import json

        # # Init mongodb and connection to MongoDB
        cluster = "mongodb+srv://alfabigdata:pw5478@cluster0mongotest.qtvn4.mongodb.net/FAO_analyzer?retryWrites=true&w=majority"
        client = MongoClient(cluster)
        db = client.FAO_analyzer
        json_dump = db.json_dump     # Collection in der Datenbank FAO-Analyzer

        def main():
            my_data_path = "daten/"     # Bitte jedes einzelne Benutzer anpassen! Lokaler Datenpfad für Ausführungen
                    
            filehandler = data_handler()     # Initialize a data_handler object for later reading and handling of the data
                    
            # # Read the data and save as a PandaFrame
            df_pop = filehandler.read_data(my_data_path + "pop_FAOSTAT_data_5-4-2021.csv")
            df_export = filehandler.read_data(my_data_path + "export_value_base_FAOSTAT_data_5-4-2021.csv")
            df_prod = filehandler.read_data(my_data_path + "production_FAOSTAT_data_5-5-2021.csv")

            # # Rename the columns: Instead of 'Values', the name of the column is changed (EVBP, Pop, Production)
            df_export = filehandler.rename_column(df_export, "EVBP")
            df_pop = filehandler.rename_column(df_pop, "Pop") 
            df_prod = filehandler.rename_column(df_prod, "Production")

            # # Save work files as Json-File:
            filehandler.save_data(df_pop)
            filehandler.save_data(df_prod)
            filehandler.save_data(df_export)

            # # Save to MongoDB:
            filehandler.dump_to_mongo(df_pop)
            filehandler.dump_to_mongo(df_prod)
            filehandler.dump_to_mongo(df_export)

            # # # Now we only want to use some of the data - Strip data to relevant parts:
            df_clean_data = filehandler.general_data(df_export, df_pop, df_prod)
            filehandler.save_data(df_clean_data)    # Saving of the new Dataframe
            filehandler.dump_to_mongo(df_clean_data)


            # # Initialize classes for plotting and analyzing
            plothandler = plotter_class()
            ana = analysis()

            ## Streamlit Execution:
            # # ---------- Headline

            # Test in local with (Terminal):    streamlit run endprojekt_final_fao_analyse.py
            st.write("Projektarbeit Gruppe E: Helena Brinkmann, Eugen Sperling und Daniel Andrade.")
            st.write("Big Data Analysis, Dozent: Thorsten Klein")
            st.write("Ziel der Arbeit: Inwieweit beeinflusst das Bevölkerungswachstum/-entwicklung den Außenhandel \
                bzw. Export eines Landes?", type = "multiline")
            st.header("**Abhängigkeit des Exports bzw. der Produktion der Agrarprodukte von der Bevölkerungsentwicklung**")
            st.write("")
            st.write("")
            st.write("FAO analyzer v1.3")

            # # ---------- Description:
            st.write("_Thesis: In wieweit beeinflusst die Bevölkerungsentwicklung das Export bzw. die Produktion von Agrarprodukte? Am Beispiel von drei Ländern, \
                ein Industrieland (Deutschland), ein Schwellenland (Brasilien) und ein Entwicklungsland (Kambodscha)._")
            st.write("Data Description:")
            st.dataframe(df_clean_data.describe())

            # # ---------- Quick glance plot:
            st.set_option('deprecation.showPyplotGlobalUse', False)     
            st.write("1. Schritt: Vergleich alle drei Ländern über die Jahren. Daten werden in einem einfachen Plot in einer \
                halblogarithmische Darstellung visualisiert")
            fig1 = plothandler.simple_plot(df_clean_data)    # Aufrufen der Klasse simple_plot
            st.pyplot(fig1)

            # # ---------- Auswahl der Daten:
            st.write("2. Schritt: Jedes Land wird einzel betrachtet. Erst wird das Export Value Base Price (Einheit: 1000 $), \
                anschließend die Prduktion (Gross Production Index Number) betrachtet.")
            st.write("_Hier wird einerseits die absolute Nummer betrachtet (zweites Schaubild), aber auch das Increment \
                Factor betrachtet, sodass die Daten um vergleichbare Skalen zu erhalten ('Normierung')._")
            my_label = st.selectbox("Wähle ein Land aus", ["Brazil","Germany", "Cambodia"])     # Hier Filtert man die Ergebnisse
            # # Nächster Schritt: Für alle Länder verallgemeinern.
            countries = [my_label]    # Speichern des gewählten Landes

            # # ---------- Analysis und Regression-Methoden

            # # Abhängigkeit von EVBP von der Population:
            st.write("**a) Abhängigkeit des Export Value Base Preis (Agricultural Products) von der Bevölkerungsentwicklung**")
            st.pyplot(ana.ols_regression("EVBP", df_clean_data, my_label))    # OLS Regression Results für das gewählte Land
            st.pyplot(plothandler.relative_data_plot(countries, df_export, df_pop, "EVBP", "Pop"))   # # Plotten der relativen Daten mit relative_data_plot
            # # Hier wird in diese Funktion eine andere Funktion aufgerufen (mit exponentielle Regression)
            st.pyplot(sns.jointplot(x="Pop", y="EVBP", data=df_clean_data[df_clean_data['Area']== my_label], kind = 'reg',fit_reg= True, size = 7))
            # # Erstellt eine lineare Regression mit den absoluten Daten

            # # Abhängigkeit von Produktion von der Population: Analog wie oben
            st.write("**b) Abhängigkeit des Produktion (Agricultural Products) von der Bevölkerungsentwicklung**")
            st.pyplot(ana.ols_regression("Production", df_clean_data, my_label))
            st.pyplot(plothandler.relative_data_plot(countries, df_prod, df_pop, "Production", "Pop"))
            st.pyplot(sns.jointplot(x="Pop", y="Production", data=df_clean_data[df_clean_data['Area']==countries[0]], kind = 'reg',fit_reg= True, size = 7))

            # # ---------- Schlussfolgerung
            st.write("**Schlussfolgerung** Hier kann man sehr gut zwischen die drei Arten Länder unterscheiden:")
            st.write("- In Brasilien, ein Schwellenland, sieht man einen eindeutigen exponentiellen Zusammenhang. Je größer die Bevölkerung, desto größer \
                die Produktion und der Export von Agrarprodukte.")
            st.write("- In Deutschland, ein Industrieland, ist der wirtschaftliche Wachtstum unabhängig von der Bevölkerungsentwicklung. Dieser wächst meist \
                kontinuierlich.")
            st.write("- In Kambodscha, ein Entwicklungsland, kann man unterschiedliches sehen. Während der Pol Pot-Diktatur gibt es kein wirtschaftlichen \
                Wachtstum, jedoch am Ende der Diktatur dieser und die Produktion stark zunehmen. ")

        class data_handler():

            def read_data(self, filename):
                """ Auslesen der Daten in ein Pandas Dataframe """
                return pd.read_csv(filename)

            def rename_column(self, dataframe, column_key):
                """ Rename der Column Value zu den entsprechenden Name """
                dataframe = dataframe.rename(columns={"Value": column_key}) 
                return dataframe

            def save_data(self, dataframe):
                """ Lokale Speicherung der Daten """
                filename = ""
                for i in dataframe.columns:
                    filename = filename + str(i) +"_"
                filename = filename.replace(" ","_")
                json_file = dataframe.to_json(f'daten/{filename}.json')

            def dump_to_mongo(self, dataframe):
                """ Speicherung der Daten zu eine MongoDB """
                data_file = dataframe.to_dict()
                result = json.loads(json.dumps(data_file))  # This construct "converts" all elements in the dict to true strings
                status = json_dump.insert(result)
                return status

            def get_from_mongo(self):
                """ Next step: Method to download files from mongoDB """
                pass

            def general_data(self, dataframe1, dataframe2, dataframe3):
                """ Erstellen von ein neues Dataframe aus den vorherigen Dataframe, sodass nur die benötigte Daten zu zeigen sind. """
                df_clean_data = dataframe1[["Area", "Year", "EVBP"]].copy()
                df_pop_new = dataframe2[["Pop"]].copy()
                df_prod_new = dataframe3[["Production"]].copy()
                df_clean_data = df_clean_data.join(df_pop_new)
                df_clean_data = df_clean_data.join(df_prod_new)
                return df_clean_data

            def relative_columnvalue(self, dataframe, country_name, column_key, liste):
                """ Hier werden die relative Daten erstellt und gespeichert """
                df = dataframe[["Area", "Year", column_key]].copy()
                df_red = df.pivot(index="Year", columns="Area", values=column_key)
                values = []
                for i in range(1961,2019):
                    values.append(df_red[country_name][i]/df_red[country_name][1961])   # Alle Daten werden auf den ersten Datensatz normiert
                liste.append(values)   #  Speicherung in einer Tabelle
                return liste

        class plotter_class():

            def __init__(self):
                self.filehandler = data_handler()
                
            def simple_plot(self , dataframe):
                """ Erstellen des Simple Plots, wo ein allgemeinen Überflick erstellt wird aus der sortierte Daten """
                fig1, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
                fig1.suptitle("Comparision of population growth and export value base price / production")
                plt1 = sns.lineplot(ax=ax1, x="Year", y="Pop", hue="Area", data=dataframe)
                plt1.set_yscale("log")
                plt2 = sns.lineplot(ax=ax2, x="Year", y="EVBP", hue="Area", data=dataframe)
                plt2.set_yscale("log")
                plt2 = sns.lineplot(ax=ax3, x="Year", y="Production", hue="Area", data=dataframe)
                plt2.set_yscale("log")
                # # Kommentar: Hier wird eine halblogarithmirung der y-Achse erstellt, damit man eine deutlichere Visualisierung hat
                return fig1

            def relative_data_plot(self, countrieslist, dataframe1, dataframe2, keynamedata1, keynamedata2):
                """ Hier wird das Plot mit dem relativen Daten erstellt, und ein exponentialer Fit draufgelegt"""
                fig1, ax = plt.subplots(1, sharex=True)
                countries_dep, countries_pop = [], []
                for i in countrieslist:
                    countries_dep = self.filehandler.relative_columnvalue(dataframe1, i, keynamedata1, countries_dep)
                    countries_pop = self.filehandler.relative_columnvalue(dataframe2, i, keynamedata2, countries_pop)
                    # # Hier wird auf die Methode: data_handler.relative_columnvalue zurückgegriffen, die die relative Daten erstellt.
                    # # Deswegen initialisiert man die data_handler-Methode zu Beginn der Klasse
                        
                # # Erstellung des exponentialles Fit: Auf Numpy ändern
                countries_dep = np.array(countries_dep)
                countries_pop = np.array(countries_pop)

                log_y_data = np.log(countries_dep[0])     # für die spätere Zurücktransformierung auf die normale Daten mit exp
                curve_fit = np.polyfit(countries_pop[0], log_y_data, 1)     # Parameter für den exponentiellen Fit werden erstellt

                y = np.exp(curve_fit[1]) * np.exp((curve_fit[0]*countries_pop[0]))     # Exponentiellen Fit
                plt.plot(countries_pop[0], countries_dep[0], ".")     # normale Plottung der Data
                plt.plot(countries_pop[0], y)      # Drauflegen des exponentiellen Fit
                plt.xlabel(f"{keynamedata2} - Increament Factor")
                plt.ylabel(f"{keynamedata1} - Increament Factor") 

        class analysis():

            def ols_regression(self, key_name, dataframe, mylabel):
                """ Erstellen der OLS-Regression für eine Kategorie mit Hilfe der ols-Methode """
                m = ols(f'{key_name} ~ Pop', dataframe[dataframe["Area"] == mylabel]).fit()

                plt.figure(6)
                plt.subplot(111)
                plt.text(0.5, 0.10, str(m.summary()), {'fontsize': 10}, fontproperties = 'monospace')    # Das ols-Fit soll als Bild gespeichert werden.
                plt.axis("off")
                plt.tight_layout()


        if __name__ == "__main__":
            main()
            # # Führt das Main-Programm (Hauptprogramm) aus
        '''
    st.code(code_text(), language='python')

class data_handler():

    def read_data(self, filename):
        """ Auslesen der Daten in ein Pandas Dataframe """
        return pd.read_csv(filename)

    def rename_column(self, dataframe, column_key):
        """ Rename der Column Value zu den entsprechenden Name """
        dataframe = dataframe.rename(columns={"Value": column_key}) 
        return dataframe

    def save_data(self, dataframe):
        """ Lokale Speicherung der Daten """
        filename = ""
        for i in dataframe.columns:
            filename = filename + str(i) +"_"
        filename = filename.replace(" ","_")
        json_file = dataframe.to_json(f'daten/{filename}.json')

    def dump_to_mongo(self, dataframe):
        """ Speicherung der Daten zu eine MongoDB """
        data_file = dataframe.to_dict()
        result = json.loads(json.dumps(data_file))  # This construct "converts" all elements in the dict to true strings
        status = json_dump.insert(result)
        return status

    def get_from_mongo(self):
        """ Next step: Method to download files from mongoDB """
        pass

    def general_data(self, dataframe1, dataframe2, dataframe3):
        """ Erstellen von ein neues Dataframe aus den vorherigen Dataframe, sodass nur die benötigte Daten zu zeigen sind. """
        df_clean_data = dataframe1[["Area", "Year", "EVBP"]].copy()
        df_pop_new = dataframe2[["Pop"]].copy()
        df_prod_new = dataframe3[["Production"]].copy()
        df_clean_data = df_clean_data.join(df_pop_new)
        df_clean_data = df_clean_data.join(df_prod_new)
        return df_clean_data

    def relative_columnvalue(self, dataframe, country_name, column_key, liste):
        """ Hier werden die relative Daten erstellt und gespeichert """
        df = dataframe[["Area", "Year", column_key]].copy()
        df_red = df.pivot(index="Year", columns="Area", values=column_key)
        values = []
        for i in range(1961,2019):
            values.append(df_red[country_name][i]/df_red[country_name][1961])   # Alle Daten werden auf den ersten Datensatz normiert
        liste.append(values)   #  Speicherung in einer Tabelle
        return liste

class plotter_class():

    def __init__(self):
        self.filehandler = data_handler()
    
    def simple_plot(self , dataframe):
        """ Erstellen des Simple Plots, wo ein allgemeinen Überflick erstellt wird aus der sortierte Daten """
        fig1, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
        fig1.suptitle("Comparision of population growth and export value base price / production")
        plt1 = sns.lineplot(ax=ax1, x="Year", y="Pop", hue="Area", data=dataframe)
        plt1.set_yscale("log")
        plt2 = sns.lineplot(ax=ax2, x="Year", y="EVBP", hue="Area", data=dataframe)
        plt2.set_yscale("log")
        plt2 = sns.lineplot(ax=ax3, x="Year", y="Production", hue="Area", data=dataframe)
        plt2.set_yscale("log")
        # # Kommentar: Hier wird eine halblogarithmirung der y-Achse erstellt, damit man eine deutlichere Visualisierung hat
        return fig1

    def relative_data_plot(self, countrieslist, dataframe1, dataframe2, keynamedata1, keynamedata2):
        """ Hier wird das Plot mit dem relativen Daten erstellt, und ein exponentialer Fit draufgelegt"""
        fig1, ax = plt.subplots(1, sharex=True)
        countries_dep, countries_pop = [], []
        for i in countrieslist:
            countries_dep = self.filehandler.relative_columnvalue(dataframe1, i, keynamedata1, countries_dep)
            countries_pop = self.filehandler.relative_columnvalue(dataframe2, i, keynamedata2, countries_pop)
            # # Hier wird auf die Methode: data_handler.relative_columnvalue zurückgegriffen, die die relative Daten erstellt.
            # # Deswegen initialisiert man die data_handler-Methode zu Beginn der Klasse
        
        # # Erstellung des exponentialles Fit: Auf Numpy ändern
        countries_dep = np.array(countries_dep)
        countries_pop = np.array(countries_pop)

        log_y_data = np.log(countries_dep[0])     # für die spätere Zurücktransformierung auf die normale Daten mit exp
        curve_fit = np.polyfit(countries_pop[0], log_y_data, 1)     # Parameter für den exponentiellen Fit werden erstellt

        y = np.exp(curve_fit[1]) * np.exp((curve_fit[0]*countries_pop[0]))     # Exponentiellen Fit
        plt.plot(countries_pop[0], countries_dep[0], ".")     # normale Plottung der Data
        plt.plot(countries_pop[0], y)      # Drauflegen des exponentiellen Fit
        plt.xlabel(f"{keynamedata2} - Increament Factor")
        plt.ylabel(f"{keynamedata1} - Increament Factor") 

class analysis():

    def ols_regression(self, key_name, dataframe, mylabel):
        """ Erstellen der OLS-Regression für eine Kategorie mit Hilfe der ols-Methode """
        m = ols(f'{key_name} ~ Pop', dataframe[dataframe["Area"] == mylabel]).fit()

        plt.figure(6)
        plt.subplot(111)
        plt.text(0.5, 0.10, str(m.summary()), {'fontsize': 10}, fontproperties = 'monospace')    # Das ols-Fit soll als Bild gespeichert werden.
        plt.axis("off")
        plt.tight_layout()


if __name__ == "__main__":
    main()
    # # Führt das Main-Programm (Hauptprogramm) aus