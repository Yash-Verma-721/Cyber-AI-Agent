async function analyze() {
    let text = document.getElementById("inputText").value;
    let langSelect = document.getElementById("langSelect");
    let language = langSelect ? langSelect.value : "English";
    console.log("Analyzing text:", text, "in language:", language);

    let btn = document.querySelector("button");
    let originalText = btn.innerText;
    btn.innerText = "Analyzing...";
    btn.disabled = true;

    try {
        let response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: text, language: language })
        });

        console.log("Response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        let data = await response.json();
        console.log("Data received:", data);
        console.log("Full API Response:", JSON.stringify(data, null, 2));

        let resultDiv = document.getElementById("result");
        let riskEl = document.getElementById("risk");
        let scoreEl = document.getElementById("score");
        let analysisEl = document.getElementById("analysis");
        let keywordsEl = document.getElementById("keywords");

        if (!resultDiv || !riskEl || !scoreEl || !analysisEl || !keywordsEl) {
            console.error("Error: One or more required DOM elements are missing.");
            return;
        }

        // Smooth animation preset
        resultDiv.style.transition = "opacity 0.4s ease-out, transform 0.4s ease-out";
        resultDiv.style.opacity = "0";
        resultDiv.style.transform = "translateY(-10px)";

        // Ensure result div is visible before inserting data
        resultDiv.classList.remove("hidden");

        // Trigger reflow to ensure animation plays
        void resultDiv.offsetWidth;

        resultDiv.style.opacity = "1";
        resultDiv.style.transform = "translateY(0)";

        // Color coding with gradients and emoji
        let emoji = "";
        let riskLevel = data?.risk || "Unknown";
        if (riskLevel === "Dangerous") {
            resultDiv.style.background = "linear-gradient(135deg, #dc2626, #991b1b)";
            emoji = "⚠️ ";
        } else if (riskLevel === "Suspicious") {
            resultDiv.style.background = "linear-gradient(135deg, #d97706, #92400e)";
            emoji = "⚡ ";
        } else {
            resultDiv.style.background = "linear-gradient(135deg, #16a34a, #166534)";
            emoji = "✅ ";
        }

        riskEl.innerText = "Risk: " + emoji + riskLevel;

        // Map Should Block to Score El since score is being deprecated by new schema
        let shouldBlock = data?.should_block ? "<span style='color: #ef4444;'>Yes</span>" : "<span style='color: #4ade80;'>No</span>";
        scoreEl.innerHTML = "<strong>Block Recommendation:</strong> " + shouldBlock;

        let displaySummary = data?.ai_summary || "No analysis available";
        let fullExplanation = data?.ai_explanation || "No advanced AI explanation available.";
        let actionStr = data?.recommended_actions && Array.isArray(data.recommended_actions) && data.recommended_actions.length > 0 ? `<br><br><strong>Recommended Actions:</strong><br>` + data.recommended_actions.map(a => `• ${a}`).join("<br>") : "";

        let summaryHtml = `
            <div style="margin-bottom: 12px;">
                <strong style="color: #e5e5e5;">Summary:</strong> <span style="color: #d4d4d4;">${displaySummary}</span>
            </div>
        `;
        
        let explanationHtml = `
            <div style="background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 8px; border-left: 3px solid #4ade80; margin-top: 10px; margin-bottom: 12px;">
                <strong style="color: #e5e5e5; display: block; margin-bottom: 4px;">Explanation:</strong>
                <span style="font-size: 14px; color: #a3a3a3;">${fullExplanation}</span>
            </div>
        `;

        analysisEl.innerHTML = summaryHtml + explanationHtml + actionStr;

        let factorsHtml = data?.risk_factors && Array.isArray(data.risk_factors) && data.risk_factors.length > 0 ? `<strong>Risk Factors:</strong><br>` + data.risk_factors.map(f => `• ${f}`).join("<br>") : "";
        let keywordsHtml = data?.detected_keywords && Array.isArray(data.detected_keywords) && data.detected_keywords.length > 0 ? `<br><br><strong>Keywords:</strong><br><div style='margin-top:4px'>` + data.detected_keywords.map(k => `<span style="background: rgba(220, 38, 38, 0.2); border: 1px solid #ef4444; color: #fca5a5; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 6px; display: inline-block;">${k}</span>`).join("") + `</div>` : "";

        keywordsEl.innerHTML = factorsHtml + keywordsHtml || "<strong>Status:</strong> Clear";
    } catch (error) {
        console.error("Error analyzing text:", error);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}
