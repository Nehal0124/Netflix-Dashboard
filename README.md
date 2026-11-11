# Netflix Data Analytics Dashboard

A Streamlit dashboard for exploring Netflix titles using Pandas and Plotly.

## Project structure

```text
Netflix_Dashboard_Project/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── netflix_titles.csv   # Add your dataset here
```

## 1. Add the dataset

Place your `netflix_titles.csv` file inside the `data` folder.

The CSV should contain the Netflix titles dataset columns, including:
`show_id`, `type`, `title`, `director`, `cast`, `country`, `date_added`,
`release_year`, `rating`, `duration`, `listed_in`, and `description`.

## 2. Open the project

Open this folder in PyCharm.

## 3. Install libraries

Open the PyCharm Terminal and run:

```bash
python -m pip install -r requirements.txt
```

## 4. Run the dashboard

In the PyCharm Terminal, run:

```bash
python -m streamlit run app.py
```

Streamlit will show a local address, usually http://localhost:8501.
Open that address in your browser if it does not open automatically.

## Dashboard features

- KPI metrics: total titles, movies, TV shows and countries
- Sidebar filters: content type, country, rating and release year
- Movies vs TV Shows pie chart
- Titles by release year
- Titles added to Netflix by year
- Top 10 countries
- Rating distribution
- Top 10 genres
- Global country map
- Search and dataset preview

## Notes

- The CSV dataset is not included in this project ZIP. Add your own copy as described above.
- Country names that are not recognized by Plotly's country-name map may not appear on the map.
