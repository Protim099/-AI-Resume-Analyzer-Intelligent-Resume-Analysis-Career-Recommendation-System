import api, { errMsg } from "../api";

export async function downloadReport(id) {
  try {
    const res = await api.get(`/analysis/${id}/report`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url; a.download = `analysis_report_${id}.pdf`; a.click();
    URL.revokeObjectURL(url);
    return null;
  } catch (e) { return errMsg(e, "Could not download the report."); }
}
