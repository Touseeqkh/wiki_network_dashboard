# 🌐 Wiki Network Dashboard

An interactive Streamlit dashboard that visualizes Wikipedia link networks among Latin American intellectuals. This tool allows you to explore the network of references (incoming and outgoing Wikipedia links), filter by gender, and examine associated metadata like occupation, nationality, and birthdate.

## 📸 Live App

👉 [Launch the app](https://wikinetworkdashboard-9powvg2cgaspgjvecyrzsv.streamlit.app/)

---

## 📁 Features

- 🔎 **Explore by Person**: Select a Latin American intellectual and explore their Wikipedia references.
- 🔄 **Incoming & Outgoing Links**: Visualize who they reference and who references them.
- 🧠 **3D Interactive Graph**: Built using Plotly and NetworkX to represent the directional graph.
- ⚧ **Gender Filtering**: Filter the network by gender (male/female/other).
- 🌍 **Metadata Display**: View nationality, occupation, and birthdate of each person.
- 📊 **Node Metrics**: In-degree, out-degree, PageRank.
- 📈 **Distributions**: Gender and occupation bar charts.

---

## 🧠 Technologies Used

- [Streamlit](https://streamlit.io/)
- [Wikipedia API](https://pypi.org/project/wikipedia-api/)
- [NetworkX](https://networkx.org/)
- [Plotly](https://plotly.com/)
- [Pandas](https://pandas.pydata.org/)

---

## 📦 File Structure

```
📁 wiki_network_dashboard/
├── streamlit_app.py         # Main Streamlit app
├── latin_american_intellectuals.csv  # Data from Wikidata
└── README.md                # You're reading this
```

---

## 📊 Dataset

The `latin_american_intellectuals.csv` file is auto-generated via a Wikidata SPARQL script and includes:

- Name
- Birthdate
- Gender
- Nationality
- Occupation
- Incoming Links Count
- Outgoing Links Count

---

## 🚀 Run Locally

```bash
git clone https://github.com/Touseeqkh/wiki_network_dashboard.git
cd wiki_network_dashboard
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## 📬 Contact

Created by **Touseeq Danish**.  
📧 Email: touseeqkhanswl@gmail.com  
🌍 [GitHub](https://github.com/Touseeqkh)  
