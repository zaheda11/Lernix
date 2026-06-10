// LERNIX - Chart.js Visual Dashboard Analytics Logic

let workloadChartInstance = null;
let creditsChartInstance = null;

function loadAnalyticsForCurriculum(currId) {
    const placeholder = document.getElementById('chart-placeholder');
    const visualizerGrid = document.getElementById('chart-visualizer-grid');

    if (!currId) {
        // Hide charts, show selector placeholder
        if (visualizerGrid) visualizerGrid.style.display = 'none';
        if (placeholder) placeholder.style.display = 'flex';
        return;
    }

    // Fetch curriculum details
    fetch(`/api/curriculum/${currId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success === false) {
                alert("Failed to load curriculum analytics.");
                return;
            }

            // Parse data for Chart.js
            const semesters = data.semesters || [];
            const labelsSem = [];
            const workloadData = [];
            const courseLabels = [];
            const creditData = [];
            const courseColors = [];

            // Preset harmonious colors for pie chart segments
            const colorPalette = [
                '#6366f1', '#06b6d4', '#a855f7', '#10b981', 
                '#f59e0b', '#ef4444', '#3b82f6', '#ec4899'
            ];

            let colorIdx = 0;

            semesters.forEach(sem => {
                const semNum = sem.semester_number;
                labelsSem.push(`Semester ${semNum}`);

                // Calculate workload: sum of weekly hours
                let semWorkload = 0;
                
                sem.courses.forEach(course => {
                    const hrs = course.weekly_hours || (course.credits * 2);
                    semWorkload += parseInt(hrs);

                    courseLabels.push(`${course.code}: ${course.name}`);
                    creditData.push(parseInt(course.credits));
                    courseColors.push(colorPalette[colorIdx % colorPalette.length]);
                    colorIdx++;
                });

                workloadData.push(semWorkload);
            });

            // Destroy existing charts to prevent rendering overlapping errors
            if (workloadChartInstance) workloadChartInstance.destroy();
            if (creditsChartInstance) creditsChartInstance.destroy();

            // Render Workload Chart (Bar)
            const ctxWorkload = document.getElementById('workloadChart').getContext('2d');
            workloadChartInstance = new Chart(ctxWorkload, {
                type: 'bar',
                data: {
                    labels: labelsSem,
                    datasets: [{
                        label: 'Weekly Hours',
                        data: workloadData,
                        backgroundColor: 'rgba(6, 182, 212, 0.4)',
                        borderColor: '#06b6d4',
                        borderWidth: 2,
                        borderRadius: 6,
                        hoverBackgroundColor: 'rgba(6, 182, 212, 0.7)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            ticks: { color: '#cbd5e1' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#cbd5e1' }
                        }
                    }
                }
            });

            // Render Credits Chart (Doughnut)
            const ctxCredits = document.getElementById('creditsChart').getContext('2d');
            creditsChartInstance = new Chart(ctxCredits, {
                type: 'doughnut',
                data: {
                    labels: courseLabels,
                    datasets: [{
                        data: creditData,
                        backgroundColor: courseColors,
                        borderColor: '#090d16',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                color: '#cbd5e1',
                                boxWidth: 12,
                                font: { size: 9 }
                            }
                        }
                    }
                }
            });

            // Transition views
            if (placeholder) placeholder.style.display = 'none';
            if (visualizerGrid) visualizerGrid.style.display = 'grid';
        })
        .catch(err => {
            console.error("Error drawing charts: ", err);
            alert("Error parsing analytics chart payload.");
        });
}
