import __utils
import storage.dynamodb_functions as db
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from io import StringIO

def clickable_progress_chart(rows: str):
    if rows is None:
        return

    json_file = StringIO(rows)
    df = pd.read_json(json_file)

    if (
        not db.Columns().lives_to_moksha in df.columns
        or not db.Columns().journal_entry in df.columns
        or not db.Columns().date in df.columns
    ):
        return

    df = df[
        [db.Columns().date, db.Columns().lives_to_moksha, db.Columns().journal_entry]
    ].dropna()
    df["Timeline"] = pd.to_datetime(df["date"])
    df["Journal"] = df[db.Columns().journal_entry].apply(
        lambda x: __utils.insert_line_breaks(x)
    )

    layout = go.Layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    fig = go.Figure(
        data=[
            go.Scatter(
                x=df["Timeline"],
                y=df[db.Columns().lives_to_moksha],
                text=df[db.Columns().journal_entry].str.slice(0, 50),
                mode="lines+markers",
                line=dict(color="gold"),
                hovertemplate="<b>%{text}</b>",
            )
        ],
        layout=layout,
    )
    fig.update_layout(
        {
            "title_text": "My progress<br><sup>on path to Moksha</sup>",
            "hoverlabel.align": "left",
            "xaxis_title": "Timeline",
            "yaxis_title": "Lives to Moksha",
        }
    )

    return pio.to_json(fig)


def clickable_score_diagram(score_df, assessment_percent_completion):
    layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True,
        showlegend=False,
    )

    moksha_row_df = score_df[score_df["category"] == "Moksha"]
    moksha_score = moksha_row_df["score"].values[0]
    score_df = score_df[score_df["category"] != "Moksha"]
    labels = score_df["category"]
    original_values = score_df["score"]
    # score_df["score"] = pd.to_numeric(score_df["score"], errors="coerce")
    score_df.loc[:, "score"] = pd.to_numeric(score_df["score"], errors="coerce")
    # custom_colors = ["#FF5733", "#33FF57", "#3357FF", "#F39C12", "#9B59B6"]
    custom_colors = ["#FF5733", "#1E90FF", "#228B22", "#D35400", "#8E44AD"]
    custom_text = [
        f"{label}:<br>{value}" for label, value in zip(labels, original_values)
    ]

    # Create donut chart (using abs value if you want positive slices)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=score_df["category"],
                values=score_df["score"].abs(),  # or .score if values are positive
                text=custom_text,
                textinfo="text",
                # "textinfo": "label+value",  // Display only the label and actual value on the chart itself
                hoverinfo="text",  # // Display only the label and actual value on hover
                hole=0.5,
                marker=dict(colors=custom_colors),
            )
        ],
        layout=layout,
    )

    # Add Moksha score as center text
    fig.update_layout(
        title_text="# of Lives to Moksha <br>and Contributing Factors",
        annotations=[
            dict(
                text=f"<b>{moksha_score}</b><br>Lives to<br> Moksha",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
            ),
            dict(
                text=f"""\u002aBased on {assessment_percent_completion}% assessment completion.""",  # Footnote text
                x=0.5,  # Center horizontally
                y=-0.2,  # Position below the donut chart
                font_size=14,
                showarrow=False,
                # font=dict(color="black"),  # Adjust color based on your theme
                align="center",
            ),
        ],
    )
    return fig.to_json()
