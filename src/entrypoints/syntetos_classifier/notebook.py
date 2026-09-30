import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import marimo as mo

    return alt, mo


@app.cell
def _():
    from core.syntetos import classify_series
    from infrastructure.syntetos_metrics import PolarsSyntetosMetrics
    from infrastructure.time_series_reader import TimeSeriesReadError, load_time_series

    return (
        PolarsSyntetosMetrics,
        TimeSeriesReadError,
        classify_series,
        load_time_series,
    )


@app.cell
def _(mo):
    mo.md("## Series classification")

    date_column = mo.ui.text(label="Date column", value="date")
    value_column = mo.ui.text(label="Value column", value="value")
    source = mo.ui.text(label="Path or URL")
    upload = mo.ui.file_uploader(label="…or upload a CSV or Parquet file")
    submit = mo.ui.submit_button(label="Classify")

    form = mo.ui.form(mo.vstack([date_column, value_column, source, upload, submit]))
    form
    return date_column, form, source, submit, upload, value_column


@app.cell
def _(
    PolarsSyntetosMetrics,
    TimeSeriesReadError,
    classify_series,
    date_column,
    form,
    load_time_series,
    source,
    submit,
    upload,
    value_column,
):
    form

    mo.stop(form.value is None, mo.md("Submit the form to classify a series."))

    typed_source = source.value.strip()
    uploaded = upload.value[0] if upload.value else None

    error = None
    if uploaded is not None and typed_source:
        error = "Provide either a path/URL or an upload, not both."
    elif uploaded is None and not typed_source:
        error = "Provide a path/URL or upload a CSV or Parquet file."

    result = None
    if error is None:
        try:
            _loaded = load_time_series(
                uploaded if uploaded is not None else typed_source,
                date_column.value.strip(),
                value_column.value.strip(),
            )
            result = (_loaded, classify_series(_loaded.values, PolarsSyntetosMetrics()))
        except TimeSeriesReadError as exc:
            error = str(exc)

    if error is not None:
        mo.ui.alert(error, kind="error")
        mo.stop(True)

    mo.stop(result is None)

    return (result,)


@app.cell
def _(alt, mo, result):
    loaded, series_type = result

    mo.ui.altair_chart(
        alt.Chart(
            alt.Data(
                values={
                    "date": loaded.dates.dt.strftime("%Y-%m-%d").tolist(),
                    "value": loaded.values.tolist(),
                }
            )
        )
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="Value"),
        )
    )

    not_classifiable = series_type.name == "NOT_CLASSIFIABLE"
    mo.callout(
        mo.vstack(
            [
                mo.md(f"## {series_type.value.title()}"),
                mo.md(
                    "This series is outside the intermittent-demand model, so it has "
                    "no Syntetos-Boylan classification."
                    if not_classifiable
                    else "Classified by average demand interval and squared "
                    "coefficient of variation."
                ),
            ]
        ),
        kind="warn" if not_classifiable else "success",
    )
    return


if __name__ == "__main__":
    app.run()
