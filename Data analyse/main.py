from flask import Flask, render_template, send_file
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time

app = Flask(__name__)

links = {"Download": "/download",
         "View raw data": "/view_raw_data",
         "Mean, Median, standard deviation": "/mean_median_standard_deviation",
         "Histogram colors of cars": "/Histogram_colors_of_cars",
         "Pie chart of brands": "/pie_chart_of_brands",
         "Scatter plot of the mileage and the price": "/scatter_plot_of_mileage_and_price",
         "Changing of the mean price depending on the year": "/changing_of_the_mean_price_depending_on_the_year",
         "Audi vs Volkswagen": "/audi_vs_volkswagen",
         "Conclusion": "/conclusion"}


def render_index(image=None, html_string=None):
    return render_template("index.html", links=links, image=image, code=time.time(), html_string=html_string)


@app.route('/', methods=['GET'])
def main_page():
    return render_index()


@app.route(links["Download"], methods=['GET'])
def download_data():
    return send_file("data/cars.csv", as_attachment=True)


@app.route(links["View raw data"], methods=['GET'])
def view_raw_data():
    df = pd.read_csv("data/cars.csv")
    return render_index(html_string=df.to_html())


@app.route(links["Mean, Median, standard deviation"], methods=['GET'])
def show_stat():
    df = pd.read_csv("data/cars.csv")
    df1 = pd.DataFrame([[df["priceUSD"].mean(), df["priceUSD"].median(), df["priceUSD"].std()],
                        [df["mileage(kilometers)"].mean(), df["mileage(kilometers)"].median(),
                         df["mileage(kilometers)"].std()],
                        [df["volume(cm3)"].mean(), df["volume(cm3)"].median(), df["volume(cm3)"].std()]],
                       index=("priceUSD", "mileage(kilometers)", "volume(cm3)"),
                       columns=("mean", "median", "standard deviation"))
    html_string = df1.to_html()
    return render_index(html_string=html_string)


@app.route(links["Histogram colors of cars"], methods=['GET'])
def show_histogram():
    df = pd.read_csv("data/cars.csv")
    plot = px.histogram(data_frame=df, x="color", title='Histogram colors of cars').update_xaxes(
        categoryorder='total descending')
    return render_index(html_string=plot.to_html(full_html=False, include_plotlyjs='cdn'))


@app.route(links["Pie chart of brands"], methods=['GET'])
def show_pie_chart():
    df = pd.read_csv("data/cars.csv")
    one = df["make"].value_counts()
    two = pd.Series(one.index, index=one.index, name='brands')
    f = pd. concat([one, two], axis=1)
    f.loc[f["make"] < 2000, 'brands'] = "other brands"
    plot = px.pie(values=f["make"], names=f["brands"], title='Pie chart of brands')
    return render_index(html_string=plot.to_html(full_html=False, include_plotlyjs='cdn'))


@app.route(links["Scatter plot of the mileage and the price"], methods=['GET'])
def show_bar_chart():
    df = pd.read_csv("data/cars.csv")
    plot = px.scatter(data_frame=df, x="mileage(kilometers)", y="priceUSD",
                      color="make", title='Scatter plot of mileage and price')
    return render_index(html_string=plot.to_html(full_html=False, include_plotlyjs='cdn'))


@app.route(links["Changing of the mean price depending on the year"], methods=['GET'])
def show_line_chart():
    df = pd.read_csv("data/cars.csv")
    df = df.query("year > 1945")
    f = df.groupby("year")["priceUSD"].mean()
    plot = px.line(f, x=f.index, y="priceUSD", title='Changing of the mean price')
    return render_index(html_string=plot.to_html(full_html=False, include_plotlyjs='cdn'))


@app.route(links["Audi vs Volkswagen"], methods=['GET'])
def show_comparison():
    df = pd.read_csv("data/cars.csv")
    df = df.sort_values("year")
    audi = df.query("make == 'audi'")
    volkswagen = df.query("make == 'volkswagen'")
    plot = go.Figure()
    plot.update_layout(title="Audi vs Volkswagen",
                       xaxis_title="Production year",
                       yaxis_title="The number of cars")
    plot.add_trace(go.Scatter(x=audi.groupby("year").count().index,
                              y=audi.groupby("year").count()["make"],
                              mode='lines+markers', name='audi'))
    plot.add_trace(go.Scatter(x=volkswagen.groupby("year").count().index,
                              y=volkswagen.groupby("year").count()["make"],
                              mode='lines+markers', name='volkswagen'))
    return render_index(html_string=plot.to_html(full_html=False, include_plotlyjs='cdn'))


@app.route(links["Conclusion"], methods=['GET'])
def make_conclusion():
    text = "This dataset represents the prices of used cars in Belarus. It includes all characteristics of the " \
           "vehicles, using car brand, model, price in USD, production year, state of the car, mileage in kilometers, " \
           "type of fuel, volume of the engine, color and transmission. From analyzing mean, medium and standard " \
           "deviation of price, mileage and volume of the engine we can infer that there are lot of cars represented " \
           "with a quite big mileage, because mean, medium and std results are quite huge. From the first histogram we " \
           "can see not only the representation of 12 defined colors and the number of cars colored in it, but also the " \
           "number of cars (3397) with other colors. It means that there is a big variety of car colors and we can " \
           "infer that the black color is the most popular. From pie chart we can infer not only that Volkswagen is the " \
           "most popular brand, but also that there is a big variety of brands on the market due to the big percent of " \
           "the part “other brands”. Scatter plot gives us information about the most common price and mileage for cars. " \
           "Usual price is under 60000 USD and usual mileage is under 600000 kilometers. " \
           "Also, Bentley has the most expensive car from this list (235235 USD). Let us look at the relationship " \
           "between the production year of the car and its cost. From the graph we can infer that that it is fluctuating " \
           "(I think it happens because we do not have a big number of cars made before 1980) at the low prices " \
           "(I think the prices are low due to a big time in usage) until approximately 1980, but after that it starts " \
           "exponentially increasing (I think it also happens due to the time in usage)." \
           "Let us finally look at the number of cars on the market from two most popular brands: Audi and Volkswagen. " \
           "We can understand from the plot that most of the years represent more Volkswagen cars than Audi. Volkswagen " \
           "and Audi reach their tops at 2008 (I think that happened, because these cars were made just " \
           "before world’s crises)."
    return render_index(html_string=text)


if __name__ == "__main__":
    app.run()
