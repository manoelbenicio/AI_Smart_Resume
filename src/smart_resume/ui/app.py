"""Streamlit web UI for Smart AI Resume."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import streamlit as st

from smart_resume.models.pipeline import PipelineRun
from smart_resume.orchestrator import Orchestrator

CATEGORY_LABELS = {
    "scale": "Scale",
    "strategic_complexity": "Strategic Complexity",
    "transformation_history": "Transformation History",
    "competitive_differentiation": "Competitive Differentiation",
    "international_experience": "International Experience",
    "career_progression_speed": "Career Progression Speed",
    "financial_impact": "Financial Impact",
    "executive_presence": "Executive Presence",
}


def _save_uploaded_file(uploaded_file: Any) -> Path:
    """Persist an uploaded file to a temporary path and return it."""
    suffix = Path(uploaded_file.name).suffix or ".txt"
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    handle.write(uploaded_file.getvalue())
    handle.flush()
    handle.close()
    return Path(handle.name)


def _render_results(state: PipelineRun) -> None:
    """Render pipeline outputs in a dashboard layout."""
    st.subheader("Benchmark Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Re-Evaluation Score", f"{state.final_score:.1f}/100")
    c2.metric("Iterations Used", str(state.iterations_used))
    c3.metric("Initial Overall Score", f"{state.scoring.overall_score:.1f}/100" if state.scoring else "n/a")
    st.caption(f"Run ID: `{state.run_id}`")

    if state.scoring:
        st.markdown("#### Market Positioning Scores")
        score_rows: list[dict[str, str]] = []
        score_dump = state.scoring.category_scores.model_dump()
        for field_name, label in CATEGORY_LABELS.items():
            score_rows.append(
                {
                    "Category": label,
                    "Score": f"{float(score_dump.get(field_name, 0)):.1f}",
                    "Explanation": state.scoring.explanations.get(field_name, ""),
                }
            )
        st.dataframe(score_rows, hide_index=True, use_container_width=True)

    if state.distinctiveness:
        st.markdown("#### Distinctiveness")
        st.write("Differentiators:")
        for item in state.distinctiveness.differentiators:
            st.write(f"- {item}")

    if state.risk_assessment:
        st.markdown("#### Risk Assessment")
        risk_rows = [
            {"Risk": key, "Level": value.level, "Explanation": value.explanation}
            for key, value in state.risk_assessment.risks.items()
        ]
        st.dataframe(risk_rows, hide_index=True, use_container_width=True)

    st.markdown("#### Improved CV (Markdown)")
    st.text_area("Generated CV", value=state.improved_cv_markdown, height=360)

    if state.output_docx_path:
        docx_path = Path(state.output_docx_path)
        if docx_path.exists():
            st.download_button(
                label="Download Improved CV (DOCX)",
                data=docx_path.read_bytes(),
                file_name=f"improved_cv_{state.run_id}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

            audit_path = docx_path.parent / "pipeline_run.json"
            if audit_path.exists():
                st.download_button(
                    label="Download Audit Trail (JSON)",
                    data=audit_path.read_bytes(),
                    file_name=f"pipeline_run_{state.run_id}.json",
                    mime="application/json",
                )


def main() -> None:
    """Render and run the Streamlit application."""
    st.set_page_config(page_title="Smart AI Resume", layout="wide")
    st.title("Smart AI Resume — Executive Benchmark Engine")
    st.write("Upload a CV and a job description to run the full 8-phase benchmark pipeline.")

    cv_file = st.file_uploader("Upload CV", type=["txt", "docx", "pdf"])
    jd_file = st.file_uploader("Upload Job Description file (optional)", type=["txt", "md"])
    jd_text = st.text_area("Or paste Job Description text", height=220)
    run_button = st.button("Run Analysis", type="primary")

    if not run_button:
        return

    if cv_file is None:
        st.error("Please upload a CV file.")
        return

    if jd_file is None and not jd_text.strip():
        st.error("Please upload a JD file or paste JD text.")
        return

    temp_paths: list[Path] = []
    try:
        cv_path = _save_uploaded_file(cv_file)
        temp_paths.append(cv_path)

        if jd_file is not None:
            jd_path = _save_uploaded_file(jd_file)
            temp_paths.append(jd_path)
            jd_input = str(jd_path)
        else:
            jd_input = jd_text.strip()

        with st.status("Running benchmark pipeline...", expanded=True) as status:
            status.write("Executing extraction, scoring, benchmark, and CV optimization phases.")
            state = Orchestrator().run(cv_input=str(cv_path), jd_input=jd_input)
            status.write("Pipeline run completed successfully.")
            status.update(label="Pipeline complete", state="complete")

        _render_results(state)

    except Exception as exc:  # noqa: BLE001
        st.error("Pipeline execution failed.")
        st.exception(exc)
    finally:
        for temp_path in temp_paths:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
