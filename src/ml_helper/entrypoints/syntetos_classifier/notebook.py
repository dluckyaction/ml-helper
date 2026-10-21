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
    date_column = mo.ui.text(label="Date column", value="date")
    value_column = mo.ui.text(label="Value column", value="value")
    source = mo.ui.text(label="Path or URL")
    upload = mo.ui.file(label="…or upload a CSV or Parquet file")

    form = mo.md(
        """
        ## Series classification

        {date_column}

        {value_column}

        {source}

        {upload}
        """
    ).batch(
        date_column=date_column,
        value_column=value_column,
        source=source,
        upload=upload,
    ).form(
        submit_button_label="Classify",
        bordered=False,
    )
    form
    return (form,)


@app.cell
def _(
    PolarsSyntetosMetrics,
    TimeSeriesReadError,
    classify_series,
    form,
    load_time_series,
    mo,
):
    import io

    form

    mo.stop(form.value is None, mo.md("Submit the form to classify a series."))

    typed_source = (form.value["source"] or "").strip()
    uploads = form.value["upload"] or ()
    uploaded = uploads[0] if uploads else None

    error = None
    if uploaded is not None and typed_source:
        error = "Provide either a path/URL or an upload, not both."
    elif uploaded is None and not typed_source:
        error = "Provide a path/URL or upload a CSV or Parquet file."

    result = None
    if error is None:
        if uploaded is not None:
            stream = io.BytesIO(uploaded.contents)
            stream.name = uploaded.name
            input_source = stream
        else:
            input_source = typed_source
        try:
            _loaded = load_time_series(
                input_source,
                (form.value["date_column"] or "").strip(),
                (form.value["value_column"] or "").strip(),
            )
            result = (_loaded, classify_series(_loaded.values, PolarsSyntetosMetrics()))
        except TimeSeriesReadError as exc:
            error = str(exc)

    if error is not None:
        mo.callout(error, kind="danger", title="Could not classify the series")
        mo.stop(True)

    return (result,)


@app.cell
def _(alt, mo, result):
    _loaded, series_type = result

    mo.ui.altair_chart(
        alt.Chart(
            alt.Data(
                values={
                    "date": _loaded.dates.dt.strftime("%Y-%m-%d").tolist(),
                    "value": _loaded.values.tolist(),
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
