// LERNIX Visual Pathways Generator

document.addEventListener('DOMContentLoaded', () => {
    const rawDataEl = document.getElementById('curriculum-data-raw');
    if (!rawDataEl) return;
    try {
        const curriculum = JSON.parse(rawDataEl.textContent);
        renderRoadmaps(curriculum);
    } catch (e) {
        console.error("Error reading curriculum JSON:", e);
    }
});

function toggleRoadmapTab(tab) {
    const prereqView = document.getElementById('roadmap-prereq-view');
    const skillsView = document.getElementById('roadmap-skills-view');
    const tabPrereqBtn = document.getElementById('tab-prereq-btn');
    const tabSkillBtn  = document.getElementById('tab-skill-btn');

    if (tab === 'prereq') {
        prereqView.style.display = 'block';
        skillsView.style.display = 'none';
        tabPrereqBtn.className = 'btn btn-primary';
        tabSkillBtn.className  = 'btn btn-secondary';
    } else {
        prereqView.style.display = 'none';
        skillsView.style.display = 'block';
        tabPrereqBtn.className = 'btn btn-secondary';
        tabSkillBtn.className  = 'btn btn-primary';
    }
}

// Sanitize any string into a safe Mermaid node ID
function safeId(str) {
    return str.replace(/[^a-zA-Z0-9]/g, '_');
}

async function renderRoadmaps(curriculum) {
    // ── 1. Prerequisite flowchart ──
    let prereqCode = "flowchart TD\n";
    prereqCode += "    classDef beginner fill:#06b6d4,stroke:#0891b2,color:#fff,stroke-width:2px\n";
    prereqCode += "    classDef intermediate fill:#6366f1,stroke:#4f46e5,color:#fff,stroke-width:2px\n";
    prereqCode += "    classDef advanced fill:#a855f7,stroke:#9333ea,color:#fff,stroke-width:2px\n\n";

    const codeToNodeId = {};   // course.code  → safe node id
    const nameToNodeId = {};   // course.name  → safe node id

    curriculum.semesters.forEach(sem => {
        prereqCode += `    subgraph SEM${sem.semester_number} ["Semester ${sem.semester_number}"]\n`;
        sem.courses.forEach(course => {
            const nid = "N_" + safeId(course.code);
            codeToNodeId[course.code] = nid;
            nameToNodeId[course.name] = nid;
            const diff = (course.difficulty || '').toLowerCase();
            const cls  = diff === 'beginner' ? 'beginner' : diff === 'intermediate' ? 'intermediate' : 'advanced';
            const label = course.code + ": " + course.name;
            prereqCode += `        ${nid}["${label}"]:::${cls}\n`;
        });
        prereqCode += "    end\n\n";
    });

    curriculum.semesters.forEach(sem => {
        sem.courses.forEach(course => {
            if (!course.prerequisites || !course.prerequisites.length) return;
            course.prerequisites.forEach(prereq => {
                const p = prereq.trim();
                const srcId = codeToNodeId[p] || nameToNodeId[p];
                const dstId = codeToNodeId[course.code];
                if (srcId && dstId) prereqCode += `    ${srcId} --> ${dstId}\n`;
            });
        });
    });

    // ── 2. Skill dependency graph ──
    let skillsCode = "flowchart LR\n";
    skillsCode += "    classDef course fill:#1e293b,stroke:#cbd5e1,color:#fff,stroke-width:1px\n";
    skillsCode += "    classDef skill fill:#10b981,stroke:#059669,color:#fff,stroke-width:1px\n\n";

    curriculum.semesters.forEach(sem => {
        sem.courses.forEach(course => {
            const cid = "C_" + safeId(course.code);
            skillsCode += `    ${cid}["${course.code}: ${course.name}"]:::course\n`;
            (course.key_skills || []).forEach((skill, si) => {
                // unique per course+skill to avoid node ID collisions
                const sid = "S_" + safeId(course.code) + "_" + si;
                skillsCode += `    ${sid}["${skill}"]:::skill\n`;
                skillsCode += `    ${cid} --> ${sid}\n`;
            });
        });
    });

    // Render both using mermaid.render (returns SVG string, works reliably)
    await renderMermaid('prereq-mermaid-graph',  prereqCode,  'prereq_graph');
    await renderMermaid('skills-mermaid-graph', skillsCode, 'skills_graph');
}

async function renderMermaid(containerId, code, graphId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    try {
        const { svg } = await mermaid.render(graphId, code);
        container.innerHTML = svg;
        // Make SVG fill the container width
        const svgEl = container.querySelector('svg');
        if (svgEl) {
            svgEl.style.width  = '100%';
            svgEl.style.height = 'auto';
            svgEl.style.maxWidth = '100%';
        }
    } catch (err) {
        console.error("Mermaid render error for", containerId, err);
        container.innerHTML = `<p style="color:#f87171;padding:1rem;">Failed to render graph. Check console for details.</p><pre style="color:#94a3b8;font-size:0.75rem;white-space:pre-wrap;">${err.message}</pre>`;
    }
}
