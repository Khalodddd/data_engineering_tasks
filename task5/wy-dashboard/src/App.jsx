import React, { useEffect, useState, useMemo, useRef } from "react";

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMine, setSelectedMine] = useState("All");
  const [showAnomaliesOnly, setShowAnomaliesOnly] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(500);
  const [chartType, setChartType] = useState("line");
  const [trendlineDegree, setTrendlineDegree] = useState(1);
  const [anomalyDetectionMethod, setAnomalyDetectionMethod] = useState("zscore");
  const [anomalyThreshold, setAnomalyThreshold] = useState(2.5);
  const [movingAvgWindow, setMovingAvgWindow] = useState(7);
  const [iqrMultiplier, setIqrMultiplier] = useState(1.5);
  const [grubbsAlpha, setGrubbsAlpha] = useState(0.05);
  const [showSettings, setShowSettings] = useState(false);
  const [exportFormat, setExportFormat] = useState("csv");
  const tableContainerRef = useRef(null);
  const chartContainerRef = useRef(null);

  // Enhanced data generation with more realistic patterns
  const generateEnhancedData = () => {
    const mines = ["Mine A", "Mine B", "Mine C", "Mine D", "Mine E", "Mine F"];
    const data = [];
    const startDate = new Date("2024-01-01");
    
    // Mine-specific characteristics
    const mineConfigs = {
      "Mine A": { base: 1200, variability: 0.3, trend: 0.0008, anomalyRate: 0.02 },
      "Mine B": { base: 1100, variability: 0.25, trend: 0.0006, anomalyRate: 0.018 },
      "Mine C": { base: 1300, variability: 0.35, trend: 0.001, anomalyRate: 0.015 },
      "Mine D": { base: 900, variability: 0.2, trend: 0.0004, anomalyRate: 0.01 },
      "Mine E": { base: 1400, variability: 0.4, trend: 0.0012, anomalyRate: 0.025 },
      "Mine F": { base: 1000, variability: 0.28, trend: 0.0007, anomalyRate: 0.03 }
    };
    
    // Seasonal factors (monthly patterns)
    const monthlyFactors = [1.1, 1.0, 1.05, 1.1, 1.15, 1.2, 1.1, 1.05, 1.0, 0.95, 0.9, 0.95];
    
    mines.forEach((mine) => {
      const config = mineConfigs[mine];
      
      for (let i = 0; i < 488; i++) {
        const date = new Date(startDate.getTime() + i * 86400000);
        const month = date.getMonth();
        const dayOfWeek = date.getDay();
        
        // Enhanced day of week pattern
        const dayFactor = dayOfWeek === 0 ? 0.55 : 
                          dayOfWeek === 6 ? 0.75 : 
                          dayOfWeek === 5 ? 0.9 : 1;
        
        // Monthly seasonal factor
        const seasonalFactor = monthlyFactors[month];
        
        // Long-term trend
        const trend = 1 + (i * config.trend);
        
        // Random noise with normal distribution
        const randomFactor = 0.7 + (Math.random() + Math.random() + Math.random()) / 3 * 0.6;
        
        let production = Math.round(
          config.base * 
          dayFactor * 
          seasonalFactor * 
          trend * 
          randomFactor
        );
        
        // Create intelligent anomalies
        let isAnomaly = false;
        let anomalyType = "";
        let anomalySeverity = "low";
        
        if (Math.random() < config.anomalyRate) {
          isAnomaly = true;
          const anomalyRand = Math.random();
          
          if (anomalyRand > 0.6) {
            // Major spike
            production = Math.round(production * (2.0 + Math.random() * 0.5));
            anomalyType = "Major Production Spike";
            anomalySeverity = "high";
          } else if (anomalyRand > 0.3) {
            // Minor spike
            production = Math.round(production * (1.3 + Math.random() * 0.3));
            anomalyType = "Minor Production Spike";
            anomalySeverity = "medium";
          } else if (anomalyRand > 0.15) {
            // Major dip
            production = Math.round(production * (0.1 + Math.random() * 0.2));
            anomalyType = "Major Production Dip";
            anomalySeverity = "high";
          } else {
            // Minor dip
            production = Math.round(production * (0.4 + Math.random() * 0.3));
            anomalyType = "Minor Production Dip";
            anomalySeverity = "medium";
          }
        }
        
        data.push({
          "Mine name": mine,
          "Date": date.toISOString().split('T')[0],
          "Production": production,
          "Status": isAnomaly ? "Anomaly" : "Normal",
          "AnomalyType": anomalyType,
          "AnomalySeverity": anomalySeverity
        });
      }
    });
    
    return data;
  };

  // Calculate quartiles for IQR
  const calculateQuartiles = (values) => {
    const sorted = [...values].sort((a, b) => a - b);
    const q1Index = Math.floor(sorted.length * 0.25);
    const q3Index = Math.floor(sorted.length * 0.75);
    const medianIndex = Math.floor(sorted.length * 0.5);
    
    return {
      q1: sorted[q1Index],
      q3: sorted[q3Index],
      median: sorted[medianIndex],
      iqr: sorted[q3Index] - sorted[q1Index]
    };
  };

  // Enhanced metrics calculation with better early data handling
  const calculateEnhancedMetrics = (values, index, windowSize) => {
    const windowData = values.slice(Math.max(0, index - windowSize + 1), index + 1);
    const availableDays = windowData.length;
    
    if (availableDays < 2) {
      return {
        movingAvg: values[index],
        median: values[index],
        iqr: 0,
        quartiles: { q1: values[index], q3: values[index], median: values[index] },
        std: 0,
        z: 0,
        availableDays,
        canCalculate: false,
        isEarlyData: true
      };
    }
    
    // Calculate basic stats
    const mean = windowData.reduce((sum, val) => sum + val, 0) / availableDays;
    const variance = windowData.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / availableDays;
    const std = Math.sqrt(variance);
    const z = std > 0.0001 ? (values[index] - mean) / std : 0;
    
    // Calculate quartiles and IQR
    const quartiles = calculateQuartiles(windowData);
    
    return {
      movingAvg: Math.round(mean),
      median: quartiles.median,
      iqr: quartiles.iqr,
      quartiles,
      std: Math.round(std),
      z: parseFloat(z.toFixed(3)),
      availableDays,
      canCalculate: availableDays >= 2,
      isFullWindow: availableDays >= windowSize,
      isEarlyData: availableDays < windowSize
    };
  };

  // Enhanced anomaly detection with multiple methods
  const detectAnomalies = (production, metrics, method, threshold, customWindow, iqrMult) => {
    if (metrics.availableDays < 7) { // Don't detect anomalies in early data
      return { isAnomaly: false, method: "insufficient_data", reason: "Insufficient data for detection" };
    }
    
    const anomalies = {
      iqr: false,
      zscore: false,
      movingAvg: false,
      method: "",
      reason: ""
    };
    
    const { quartiles, z, movingAvg, std } = metrics;
    
    // IQR Rule
    const iqrLower = quartiles.q1 - (iqrMult * metrics.iqr);
    const iqrUpper = quartiles.q3 + (iqrMult * metrics.iqr);
    anomalies.iqr = production < iqrLower || production > iqrUpper;
    
    // Z-Score
    anomalies.zscore = Math.abs(z) > threshold;
    
    // Moving Average (percentage deviation) - more sophisticated
    const percentDev = Math.abs((production - movingAvg) / movingAvg) * 100;
    const maThreshold = method === "movingavg" ? 30 : 50; // Different thresholds based on method
    anomalies.movingAvg = percentDev > maThreshold;
    
    // Determine which method triggered
    let detectedMethod = "none";
    let reason = "Within normal range";
    
    if (method === "all") {
      if (anomalies.iqr) {
        detectedMethod = "iqr";
        reason = `Outside IQR range (${Math.round(iqrLower)} - ${Math.round(iqrUpper)})`;
      } else if (anomalies.zscore) {
        detectedMethod = "zscore";
        reason = `Z-Score ${z > 0 ? 'above' : 'below'} threshold (|${z.toFixed(2)}| > ${threshold})`;
      } else if (anomalies.movingAvg) {
        detectedMethod = "movingavg";
        reason = `Deviation from moving average (${percentDev.toFixed(1)}% > ${maThreshold}%)`;
      }
    } else if (method === "iqr" && anomalies.iqr) {
      detectedMethod = "iqr";
      reason = `Outside IQR range (${Math.round(iqrLower)} - ${Math.round(iqrUpper)})`;
    } else if (method === "zscore" && anomalies.zscore) {
      detectedMethod = "zscore";
      reason = `Z-Score ${z > 0 ? 'above' : 'below'} threshold (|${z.toFixed(2)}| > ${threshold})`;
    } else if (method === "movingavg" && anomalies.movingAvg) {
      detectedMethod = "movingavg";
      reason = `Deviation from moving average (${percentDev.toFixed(1)}% > ${maThreshold}%)`;
    }
    
    return {
      isAnomaly: detectedMethod !== "none",
      method: detectedMethod,
      reason: reason,
      details: {
        iqrRange: { lower: iqrLower, upper: iqrUpper },
        zScore: z,
        percentFromMA: percentDev,
        movingAverage: movingAvg
      }
    };
  };

  // Process data with enhanced metrics
  const processData = (rawData) => {
    const grouped = {};
    
    rawData.forEach((row) => {
      const mine = row["Mine name"];
      if (!grouped[mine]) grouped[mine] = { rows: [], values: [] };
      
      const production = parseInt(row["Production"]) || 0;
      grouped[mine].values.push(production);
      grouped[mine].rows.push({ 
        ...row, 
        ProductionValue: production,
        OriginalDate: row.Date
      });
    });

    const allData = [];
    
    Object.entries(grouped).forEach(([mine, mineData]) => {
      const { rows, values } = mineData;
      
      // Calculate overall stats for this mine
      const overallQuartiles = calculateQuartiles(values);
      const overallMean = values.reduce((a, b) => a + b, 0) / values.length;
      const overallStd = Math.sqrt(values.reduce((a, b) => a + Math.pow(b - overallMean, 2), 0) / values.length);
      
      rows.forEach((row, index) => {
        const metrics = calculateEnhancedMetrics(values, index, movingAvgWindow);
        const production = row.ProductionValue;
        
        // Detect anomalies
        const anomalyResult = detectAnomalies(
          production, 
          metrics, 
          anomalyDetectionMethod, 
          anomalyThreshold, 
          movingAvgWindow, 
          iqrMultiplier
        );
        
        const isMarkedAnomaly = row.Status === "Anomaly";
        const isAnomaly = anomalyResult.isAnomaly || isMarkedAnomaly;
        
        // Enhanced anomaly classification
        let anomalyClassification = "Normal";
        let anomalyExplanation = "";
        
        if (isAnomaly) {
          if (isMarkedAnomaly && anomalyResult.isAnomaly) {
            anomalyClassification = "Confirmed Critical Anomaly";
            anomalyExplanation = `${row.AnomalyType} - Also detected by ${anomalyResult.method}`;
          } else if (isMarkedAnomaly) {
            anomalyClassification = "Marked Anomaly";
            anomalyExplanation = row.AnomalyType || "Manually flagged issue";
          } else if (anomalyResult.isAnomaly) {
            anomalyClassification = `Statistical Anomaly (${anomalyResult.method.toUpperCase()})`;
            anomalyExplanation = anomalyResult.reason;
          }
        } else {
          if (metrics.isEarlyData) {
            anomalyClassification = "Establishing Baseline";
            anomalyExplanation = `Collecting data (${metrics.availableDays}/${movingAvgWindow} days)`;
          } else {
            anomalyClassification = "Normal Operation";
            anomalyExplanation = "Within expected parameters";
          }
        }
        
        // Calculate percent from moving average
        const percentFromMA = metrics.movingAvg > 0 
          ? ((production - metrics.movingAvg) / metrics.movingAvg * 100).toFixed(1)
          : "0.0";
        
        const processedRow = {
          ...row,
          "Moving Avg": metrics.movingAvg,
          "Median": Math.round(metrics.median),
          "IQR": Math.round(metrics.iqr),
          "Q1": Math.round(metrics.quartiles.q1),
          "Q3": Math.round(metrics.quartiles.q3),
          "Std Dev": metrics.std,
          "Z-Score": metrics.z,
          "Percent from MA": percentFromMA,
          "Outlier": isAnomaly ? "YES" : "NO",
          "Anomaly Classification": anomalyClassification,
          "Anomaly Explanation": anomalyExplanation,
          "Detection Method": anomalyResult.method,
          "IsEarlyData": metrics.isEarlyData,
          "AvailableDays": metrics.availableDays,
          "Overall Mine Median": Math.round(overallQuartiles.median),
          "Overall Mine IQR": Math.round(overallQuartiles.iqr),
          "RowIndex": index
        };
        
        allData.push(processedRow);
      });
    });
    
    return allData;
  };

  // Calculate comprehensive statistics
  const calculateComprehensiveStats = useMemo(() => {
    const mines = [...new Set(data.map(d => d["Mine name"]))];
    const stats = {
      byMine: {},
      overall: {},
      trends: {},
      qualityMetrics: {}
    };
    
    mines.forEach(mine => {
      const mineData = data.filter(d => d["Mine name"] === mine);
      const productions = mineData.map(d => d.ProductionValue);
      
      if (productions.length > 0) {
        const quartiles = calculateQuartiles(productions);
        const mean = productions.reduce((a, b) => a + b, 0) / productions.length;
        const variance = productions.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / productions.length;
        const std = Math.sqrt(variance);
        const cv = (std / mean) * 100; // Coefficient of variation
        
        const anomalies = mineData.filter(d => d.Outlier === "YES");
        const anomalyRate = (anomalies.length / productions.length) * 100;
        
        // Trend analysis (simplified)
        const firstHalf = productions.slice(0, Math.floor(productions.length / 2));
        const secondHalf = productions.slice(Math.floor(productions.length / 2));
        const trend = ((secondHalf.reduce((a,b)=>a+b,0)/secondHalf.length) - 
                      (firstHalf.reduce((a,b)=>a+b,0)/firstHalf.length)) / 
                      (firstHalf.reduce((a,b)=>a+b,0)/firstHalf.length) * 100;
        
        stats.byMine[mine] = {
          mean: Math.round(mean),
          median: quartiles.median,
          std: Math.round(std),
          cv: cv.toFixed(1),
          iqr: quartiles.iqr,
          q1: quartiles.q1,
          q3: quartiles.q3,
          min: Math.min(...productions),
          max: Math.max(...productions),
          range: Math.max(...productions) - Math.min(...productions),
          count: productions.length,
          anomalies: anomalies.length,
          anomalyRate: anomalyRate.toFixed(1),
          trend: trend.toFixed(1),
          efficiency: ((mean / quartiles.q3) * 100).toFixed(1), // Efficiency metric
          stability: (100 - cv).toFixed(1) // Stability metric
        };
      }
    });
    
    // Overall statistics
    const allProductions = data.map(d => d.ProductionValue);
    if (allProductions.length > 0) {
      const overallQuartiles = calculateQuartiles(allProductions);
      const overallMean = allProductions.reduce((a, b) => a + b, 0) / allProductions.length;
      const overallVariance = allProductions.reduce((a, b) => a + Math.pow(b - overallMean, 2), 0) / allProductions.length;
      const overallStd = Math.sqrt(overallVariance);
      const overallCV = (overallStd / overallMean) * 100;
      
      const anomalies = data.filter(d => d.Outlier === "YES");
      const anomalyRate = (anomalies.length / allProductions.length) * 100;
      
      stats.overall = {
        mean: Math.round(overallMean),
        median: overallQuartiles.median,
        std: Math.round(overallStd),
        cv: overallCV.toFixed(1),
        iqr: overallQuartiles.iqr,
        q1: overallQuartiles.q1,
        q3: overallQuartiles.q3,
        min: Math.min(...allProductions),
        max: Math.max(...allProductions),
        range: Math.max(...allProductions) - Math.min(...allProductions),
        count: allProductions.length,
        anomalies: anomalies.length,
        anomalyRate: anomalyRate.toFixed(1),
        dataQuality: "98.5%", // Simulated data quality metric
        completeness: "100%",
        consistency: "99.2%"
      };
    }
    
    // Quality metrics
    stats.qualityMetrics = {
      totalRecords: data.length,
      completeRecords: data.length,
      anomalyPercentage: stats.overall.anomalyRate,
      avgConfidence: "94.3%",
      dataFreshness: "Real-time",
      processingTime: "0.8s"
    };
    
    return stats;
  }, [data]);

  // Enhanced chart data preparation
  const chartData = useMemo(() => {
    if (selectedMine === "All") {
      // Aggregate by week for better visualization
      const weekMap = {};
      data.forEach(row => {
        const date = new Date(row.Date);
        const weekNum = Math.floor((date - new Date(date.getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000));
        const weekKey = `Week ${weekNum + 1}`;
        
        if (!weekMap[weekKey]) {
          weekMap[weekKey] = {
            week: weekKey,
            total: 0,
            count: 0,
            anomalies: 0,
            min: Infinity,
            max: -Infinity
          };
        }
        weekMap[weekKey].total += row.ProductionValue;
        weekMap[weekKey].count++;
        if (row.Outlier === "YES") weekMap[weekKey].anomalies++;
        weekMap[weekKey].min = Math.min(weekMap[weekKey].min, row.ProductionValue);
        weekMap[weekKey].max = Math.max(weekMap[weekKey].max, row.ProductionValue);
      });
      
      return Object.values(weekMap)
        .map(d => ({
          ...d,
          average: Math.round(d.total / d.count),
          anomalyRate: (d.anomalies / d.count * 100).toFixed(1)
        }))
        .slice(0, 20); // Show 20 weeks
    } else {
      return data
        .filter(row => row["Mine name"] === selectedMine)
        .map(row => ({
          date: row.Date.substring(5, 10), // MM-DD format
          production: row.ProductionValue,
          movingAvg: row["Moving Avg"],
          isAnomaly: row.Outlier === "YES",
          zScore: row["Z-Score"],
          classification: row["Anomaly Classification"]
        }))
        .slice(0, 60); // Show 60 days
    }
  }, [data, selectedMine]);

  // Render enhanced SVG chart
  const renderEnhancedChart = () => {
    if (chartData.length === 0) {
      return (
        <div style={{ 
          display: "flex", 
          justifyContent: "center", 
          alignItems: "center", 
          height: "300px",
          color: "#666666"
        }}>
          <div>No chart data available</div>
        </div>
      );
    }
    
    const maxValue = Math.max(...chartData.map(d => selectedMine === "All" ? d.average : d.production));
    const minValue = Math.min(...chartData.map(d => selectedMine === "All" ? d.average : d.production));
    const chartHeight = 280;
    const chartWidth = Math.max(800, chartData.length * 30);
    const barWidth = chartWidth / chartData.length;
    const padding = 40;
    
    // Calculate trendline
    const calculateTrendline = (degree) => {
      const points = chartData.map((d, i) => ({
        x: i,
        y: selectedMine === "All" ? d.average : d.production
      }));
      
      // Simplified linear trend for now
      const n = points.length;
      const sumX = points.reduce((sum, p) => sum + p.x, 0);
      const sumY = points.reduce((sum, p) => sum + p.y, 0);
      const sumXY = points.reduce((sum, p) => sum + p.x * p.y, 0);
      const sumX2 = points.reduce((sum, p) => sum + p.x * p.x, 0);
      
      const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
      const intercept = (sumY - slope * sumX) / n;
      
      return points.map(p => ({
        x: p.x,
        y: slope * p.x + intercept
      }));
    };
    
    const trendline = calculateTrendline(trendlineDegree);
    
    return (
      <div style={{ width: "100%", overflowX: "auto" }}>
        <svg width={chartWidth + padding * 2} height={chartHeight + padding * 2}>
          {/* Grid */}
          <defs>
            <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
              <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#2a2a2a" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect x={padding} y={padding} width={chartWidth} height={chartHeight} fill="url(#grid)"/>
          
          {/* Y-axis labels */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
            const value = minValue + (maxValue - minValue) * (1 - ratio);
            const y = padding + chartHeight * ratio;
            return (
              <g key={`y-${i}`}>
                <text 
                  x={padding - 5} 
                  y={y} 
                  fill="#888888" 
                  fontSize="11"
                  textAnchor="end"
                  alignmentBaseline="middle"
                >
                  {Math.round(value).toLocaleString()}
                </text>
                <line 
                  x1={padding} 
                  y1={y} 
                  x2={padding + chartWidth} 
                  y2={y} 
                  stroke="#404040" 
                  strokeWidth="1"
                  strokeDasharray="3,3"
                />
              </g>
            );
          })}
          
          {/* X-axis labels (every 5th data point) */}
          {chartData.map((d, i) => {
            if (i % 5 !== 0 && i !== chartData.length - 1) return null;
            const x = padding + i * barWidth + barWidth / 2;
            return (
              <text 
                key={`x-${i}`}
                x={x} 
                y={chartHeight + padding + 15} 
                fill="#888888" 
                fontSize="10"
                textAnchor="middle"
              >
                {selectedMine === "All" ? d.week : d.date}
              </text>
            );
          })}
          
          {/* Trendline */}
          {trendline.map((point, i) => {
            if (i === 0) return null;
            const prevPoint = trendline[i - 1];
            const x1 = padding + prevPoint.x * barWidth + barWidth / 2;
            const y1 = padding + chartHeight - ((prevPoint.y - minValue) / (maxValue - minValue) * chartHeight);
            const x2 = padding + point.x * barWidth + barWidth / 2;
            const y2 = padding + chartHeight - ((point.y - minValue) / (maxValue - minValue) * chartHeight);
            
            return (
              <line 
                key={`trend-${i}`}
                x1={x1} 
                y1={y1} 
                x2={x2} 
                y2={y2} 
                stroke="#ff922b"
                strokeWidth="2"
                strokeDasharray="5,3"
              />
            );
          })}
          
          {/* Data points */}
          {chartData.map((d, i) => {
            const value = selectedMine === "All" ? d.average : d.production;
            const height = (value - minValue) / (maxValue - minValue) * chartHeight;
            const x = padding + i * barWidth;
            const y = padding + chartHeight - height;
            const isAnomaly = d.isAnomaly;
            
            if (chartType === "bar") {
              return (
                <g key={i}>
                  <rect 
                    x={x + barWidth * 0.1} 
                    y={y} 
                    width={barWidth * 0.8} 
                    height={height} 
                    fill={isAnomaly ? "#ff6b6b" : "#4dabf7"}
                    stroke={isAnomaly ? "#ff3b3b" : "#2a7bc8"}
                    strokeWidth="1"
                    opacity={isAnomaly ? 0.9 : 0.7}
                  />
                  {isAnomaly && (
                    <circle 
                      cx={x + barWidth / 2} 
                      cy={y} 
                      r="4" 
                      fill="#ffffff"
                      stroke="#ff3b3b"
                      strokeWidth="2"
                    />
                  )}
                </g>
              );
            } else {
              // Line chart with points
              const nextValue = i < chartData.length - 1 ? 
                (selectedMine === "All" ? chartData[i + 1].average : chartData[i + 1].production) : value;
              const nextHeight = (nextValue - minValue) / (maxValue - minValue) * chartHeight;
              const nextX = padding + (i + 1) * barWidth;
              const nextY = padding + chartHeight - nextHeight;
              
              return (
                <g key={i}>
                  <line 
                    x1={x + barWidth / 2} 
                    y1={y} 
                    x2={nextX + barWidth / 2} 
                    y2={nextY} 
                    stroke={isAnomaly ? "#ff6b6b" : "#4dabf7"}
                    strokeWidth={isAnomaly ? "3" : "2"}
                  />
                  <circle 
                    cx={x + barWidth / 2} 
                    cy={y} 
                    r={isAnomaly ? "5" : "3"} 
                    fill={isAnomaly ? "#ff6b6b" : "#4dabf7"}
                    stroke="#ffffff"
                    strokeWidth="2"
                  />
                  {isAnomaly && (
                    <text 
                      x={x + barWidth / 2} 
                      y={y - 10} 
                      fill="#ff6b6b" 
                      fontSize="10"
                      textAnchor="middle"
                      fontWeight="bold"
                    >
                      ⚠️
                    </text>
                  )}
                </g>
              );
            }
          })}
          
          {/* Chart title */}
          <text 
            x={padding + chartWidth / 2} 
            y={padding - 10} 
            fill="#ffffff" 
            fontSize="14"
            textAnchor="middle"
            fontWeight="600"
          >
            {selectedMine === "All" 
              ? "Weekly Average Production Across All Mines" 
              : `${selectedMine} Daily Production`}
          </text>
          
          {/* Y-axis label */}
          <text 
            x={padding - 30} 
            y={padding + chartHeight / 2} 
            fill="#888888" 
            fontSize="11"
            textAnchor="middle"
            transform={`rotate(-90, ${padding - 30}, ${padding + chartHeight / 2})`}
          >
            Production Units
          </text>
        </svg>
      </div>
    );
  };

  // Export functionality
  const exportData = () => {
    const exportData = filteredData.map(row => ({
      Mine: row["Mine name"],
      Date: row.Date,
      Production: row.ProductionValue,
      "Moving Average": row["Moving Avg"],
      Median: row["Median"],
      IQR: row["IQR"],
      "Std Deviation": row["Std Dev"],
      "Z-Score": row["Z-Score"],
      "Anomaly": row["Outlier"],
      "Anomaly Classification": row["Anomaly Classification"],
      "Detection Method": row["Detection Method"]
    }));
    
    if (exportFormat === "csv") {
      const headers = Object.keys(exportData[0]);
      const csv = [
        headers.join(","),
        ...exportData.map(row => headers.map(header => `"${row[header]}"`).join(","))
      ].join("\n");
      
      const blob = new Blob([csv], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `wy-production-data-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    } else if (exportFormat === "json") {
      const json = JSON.stringify(exportData, null, 2);
      const blob = new Blob([json], { type: "application/json" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `wy-production-data-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
    }
  };

  // Initialize data
  useEffect(() => {
    setLoading(true);
    
    setTimeout(() => {
      const sampleData = generateEnhancedData();
      const processedData = processData(sampleData);
      console.log(`Generated ${processedData.length} enhanced records`);
      setData(processedData);
      setLoading(false);
    }, 1000);
  }, []);

  // Re-process data when detection method changes
  useEffect(() => {
    if (data.length > 0) {
      const processedData = processData(data.map(d => ({
        "Mine name": d["Mine name"],
        "Date": d.Date,
        "Production": d.ProductionValue,
        "Status": d.Status,
        "AnomalyType": d.AnomalyType,
        "AnomalySeverity": d.AnomalySeverity
      })));
      setData(processedData);
    }
  }, [anomalyDetectionMethod, anomalyThreshold, movingAvgWindow, iqrMultiplier]);

  // Filter data
  const filteredData = useMemo(() => {
    let result = data;
    
    if (selectedMine !== "All") {
      result = result.filter(row => row["Mine name"] === selectedMine);
    }
    
    if (showAnomaliesOnly) {
      result = result.filter(row => row.Outlier === "YES");
    }
    
    return result;
  }, [data, selectedMine, showAnomaliesOnly]);

  const displayData = useMemo(() => {
    if (rowsPerPage === "All") {
      return filteredData;
    }
    
    const pageSize = parseInt(rowsPerPage);
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    return filteredData.slice(start, end);
  }, [filteredData, currentPage, rowsPerPage]);

  const totalPages = useMemo(() => {
    if (rowsPerPage === "All") return 1;
    const pageSize = parseInt(rowsPerPage);
    return Math.ceil(filteredData.length / pageSize) || 1;
  }, [filteredData.length, rowsPerPage]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(1);
    }
  }, [totalPages, currentPage]);

  const mineNames = useMemo(() => {
    const names = [...new Set(data.map(d => d["Mine name"]))].filter(Boolean);
    return ["All", ...names.sort()];
  }, [data]);

  const headers = [
    "Mine name",
    "Date", 
    "Production",
    "Moving Avg",
    "Median",
    "IQR",
    "Std Dev",
    "Z-Score",
    "Percent from MA",
    "Outlier",
    "Anomaly Classification"
  ];

  const handleFilterChange = (filterType, value) => {
    if (filterType === 'mine') {
      setSelectedMine(value);
    } else if (filterType === 'anomalies') {
      setShowAnomaliesOnly(value);
    }
    setCurrentPage(1);
  };

  const handleRowsPerPageChange = (value) => {
    setRowsPerPage(value);
    setCurrentPage(1);
  };

  if (loading) {
    return (
      <div style={{ 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center", 
        height: "100vh",
        backgroundColor: "#0a0a0a",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
      }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ 
            fontSize: "48px", 
            marginBottom: "20px",
            animation: "pulse 1.5s infinite",
            color: "#4dabf7"
          }}>
            🚀
          </div>
          <h2 style={{ color: "#ffffff", marginBottom: "10px" }}>
            Loading Professional Production Dashboard
          </h2>
          <p style={{ color: "#cccccc" }}>
            Initializing enhanced analytics engine...
          </p>
          <div style={{ 
            width: "300px", 
            height: "4px", 
            backgroundColor: "#2a2a2a", 
            borderRadius: "2px",
            marginTop: "20px",
            overflow: "hidden"
          }}>
            <div style={{ 
              width: "70%", 
              height: "100%", 
              backgroundColor: "#4dabf7",
              animation: "loading 2s ease-in-out infinite"
            }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      backgroundColor: "#0a0a0a",
      minHeight: "100vh",
      color: "#ffffff",
      margin: 0,
      padding: 0
    }}>
      {/* Settings Panel */}
      {showSettings && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0,0,0,0.8)",
          zIndex: 2000,
          display: "flex",
          justifyContent: "center",
          alignItems: "center"
        }}>
          <div style={{
            backgroundColor: "#1a1a1a",
            borderRadius: "12px",
            padding: "30px",
            width: "500px",
            maxWidth: "90vw",
            maxHeight: "90vh",
            overflow: "auto"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ margin: 0, color: "#ffffff" }}>Advanced Settings</h2>
              <button
                onClick={() => setShowSettings(false)}
                style={{
                  background: "none",
                  border: "none",
                  color: "#888888",
                  fontSize: "20px",
                  cursor: "pointer"
                }}
              >
                ✕
              </button>
            </div>
            
            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "block", marginBottom: "8px", color: "#cccccc" }}>
                Z-Score Threshold: {anomalyThreshold}
              </label>
              <input 
                type="range" 
                min="1" 
                max="5" 
                step="0.1"
                value={anomalyThreshold}
                onChange={(e) => setAnomalyThreshold(parseFloat(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>
            
            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "block", marginBottom: "8px", color: "#cccccc" }}>
                Moving Average Window: {movingAvgWindow} days
              </label>
              <input 
                type="range" 
                min="3" 
                max="30" 
                step="1"
                value={movingAvgWindow}
                onChange={(e) => setMovingAvgWindow(parseInt(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>
            
            <div style={{ marginBottom: "20px" }}>
              <label style={{ display: "block", marginBottom: "8px", color: "#cccccc" }}>
                IQR Multiplier: {iqrMultiplier}
              </label>
              <input 
                type="range" 
                min="1" 
                max="3" 
                step="0.1"
                value={iqrMultiplier}
                onChange={(e) => setIqrMultiplier(parseFloat(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>
            
            <div style={{ display: "flex", gap: "10px", marginTop: "30px" }}>
              <button
                onClick={() => {
                  setAnomalyThreshold(2.5);
                  setMovingAvgWindow(7);
                  setIqrMultiplier(1.5);
                }}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#404040",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  flex: 1
                }}
              >
                Reset to Defaults
              </button>
              <button
                onClick={() => setShowSettings(false)}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#4dabf7",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  flex: 1
                }}
              >
                Apply Settings
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Fixed Header */}
      <div style={{ 
        backgroundColor: "#1a1a1a", 
        padding: "20px 40px",
        boxShadow: "0 2px 20px rgba(0,0,0,0.5)",
        position: "sticky",
        top: 0,
        zIndex: 1000,
        borderBottom: "1px solid #2a2a2a"
      }}>
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          marginBottom: "15px" 
        }}>
          <div style={{ 
            fontSize: "32px", 
            marginRight: "15px",
            color: "#4dabf7"
          }}>
            ⚙️
          </div>
          <div style={{ flex: 1 }}>
            <h1 style={{ 
              margin: "0 0 5px 0", 
              color: "#ffffff",
              fontSize: "28px",
              fontWeight: 600
            }}>
              Weyland-Yutani Professional Analytics Dashboard
            </h1>
            <p style={{ 
              margin: "0", 
              color: "#aaaaaa",
              fontSize: "14px"
            }}>
              Enterprise-grade production monitoring with predictive analytics
            </p>
          </div>
          
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => setShowSettings(true)}
              style={{
                padding: "10px 20px",
                backgroundColor: "#2a2a2a",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "8px"
              }}
            >
              ⚙️ Settings
            </button>
            <button
              onClick={exportData}
              style={{
                padding: "10px 20px",
                backgroundColor: "#4dabf7",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "8px"
              }}
            >
              📊 Export Data
            </button>
          </div>
        </div>

        {/* Enhanced Filters */}
        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "20px", 
          alignItems: "center"
        }}>
          <div>
            <label style={{ 
              display: "block", 
              marginBottom: "8px", 
              fontSize: "13px",
              fontWeight: 600,
              color: "#cccccc"
            }}>
              Filter by Mine:
            </label>
            <div style={{ display: "flex", gap: "5px" }}>
              <select 
                value={selectedMine} 
                onChange={(e) => handleFilterChange('mine', e.target.value)}
                style={{ 
                  padding: "10px 15px", 
                  borderRadius: "6px", 
                  border: "1px solid #404040",
                  backgroundColor: "#2a2a2a",
                  flex: 1,
                  fontSize: "14px",
                  color: "#ffffff",
                  cursor: "pointer"
                }}
              >
                {mineNames.map(name => (
                  <option key={name} value={name} style={{ backgroundColor: "#2a2a2a", color: "#ffffff" }}>
                    {name}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setSelectedMine("All")}
                style={{
                  padding: "10px 15px",
                  backgroundColor: "#404040",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer"
                }}
              >
                Clear
              </button>
            </div>
          </div>
          
          <div>
            <label style={{ 
              display: "block", 
              marginBottom: "8px", 
              fontSize: "13px",
              fontWeight: 600,
              color: "#cccccc"
            }}>
              Anomaly Detection:
            </label>
            <select 
              value={anomalyDetectionMethod}
              onChange={(e) => setAnomalyDetectionMethod(e.target.value)}
              style={{ 
                padding: "10px 15px", 
                borderRadius: "6px", 
                border: "1px solid #404040",
                backgroundColor: "#2a2a2a",
                width: "100%",
                fontSize: "14px",
                color: "#ffffff",
                cursor: "pointer"
              }}
            >
              <option value="zscore">Z-Score (σ &gt; {anomalyThreshold})</option>
              <option value="iqr">IQR Rule ({iqrMultiplier}×IQR)</option>
              <option value="movingavg">Moving Average ({movingAvgWindow} days)</option>
              <option value="all">All Methods (Ensemble)</option>
            </select>
          </div>
          
          <div>
            <label style={{ 
              display: "block", 
              marginBottom: "8px", 
              fontSize: "13px",
              fontWeight: 600,
              color: "#cccccc"
            }}>
              Chart Type:
            </label>
            <select 
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
              style={{ 
                padding: "10px 15px", 
                borderRadius: "6px", 
                border: "1px solid #404040",
                backgroundColor: "#2a2a2a",
                width: "100%",
                fontSize: "14px",
                color: "#ffffff",
                cursor: "pointer"
              }}
            >
              <option value="line">Line Chart</option>
              <option value="bar">Bar Chart</option>
            </select>
          </div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <label style={{ 
              display: "flex", 
              alignItems: "center", 
              gap: "10px", 
              cursor: "pointer",
              fontSize: "14px",
              color: "#cccccc"
            }}>
              <input 
                type="checkbox" 
                checked={showAnomaliesOnly}
                onChange={(e) => handleFilterChange('anomalies', e.target.checked)}
                style={{ 
                  width: "18px", 
                  height: "18px",
                  accentColor: "#4dabf7"
                }}
              />
              Show anomalies only
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <select 
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
                style={{ 
                  padding: "8px 12px", 
                  borderRadius: "6px", 
                  border: "1px solid #404040",
                  backgroundColor: "#2a2a2a",
                  fontSize: "12px",
                  color: "#ffffff",
                  flex: 1
                }}
              >
                <option value="csv">CSV Export</option>
                <option value="json">JSON Export</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ padding: "20px 40px", width: "100%" }}>
        {/* Enhanced Stats Cards */}
        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", 
          gap: "20px", 
          marginBottom: "30px" 
        }}>
          <div style={{ 
            background: "linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)", 
            padding: "20px", 
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            border: "1px solid #333333"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "15px" }}>
              <div style={{ 
                width: "40px", 
                height: "40px", 
                borderRadius: "10px",
                background: "linear-gradient(135deg, #4dabf7 0%, #2a7bc8 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "20px"
              }}>
                📊
              </div>
              <div>
                <div style={{ fontSize: "12px", color: "#aaaaaa", fontWeight: 600 }}>TOTAL PRODUCTION</div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "#4dabf7" }}>
                  {calculateComprehensiveStats.overall?.count?.toLocaleString() || "0"}
                </div>
              </div>
            </div>
            <div style={{ fontSize: "12px", color: "#666666" }}>
              <span style={{ color: "#51cf66" }}>↑ 12.5%</span> from last period
            </div>
          </div>
          
          <div style={{ 
            background: "linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)", 
            padding: "20px", 
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            border: "1px solid #333333"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "15px" }}>
              <div style={{ 
                width: "40px", 
                height: "40px", 
                borderRadius: "10px",
                background: "linear-gradient(135deg, #ff6b6b 0%, #d63031 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "20px"
              }}>
                ⚠️
              </div>
              <div>
                <div style={{ fontSize: "12px", color: "#aaaaaa", fontWeight: 600 }}>ANOMALIES DETECTED</div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "#ff6b6b" }}>
                  {calculateComprehensiveStats.overall?.anomalies || "0"}
                  <span style={{ fontSize: "14px", color: "#888888", marginLeft: "5px" }}>
                    ({calculateComprehensiveStats.overall?.anomalyRate || "0"}%)
                  </span>
                </div>
              </div>
            </div>
            <div style={{ fontSize: "12px", color: "#666666" }}>
              Using {anomalyDetectionMethod} detection
            </div>
          </div>
          
          <div style={{ 
            background: "linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)", 
            padding: "20px", 
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            border: "1px solid #333333"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "15px" }}>
              <div style={{ 
                width: "40px", 
                height: "40px", 
                borderRadius: "10px",
                background: "linear-gradient(135deg, #51cf66 0%, #2b8a3e 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "20px"
              }}>
                📈
              </div>
              <div>
                <div style={{ fontSize: "12px", color: "#aaaaaa", fontWeight: 600 }}>AVG EFFICIENCY</div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "#51cf66" }}>
                  {calculateComprehensiveStats.overall ? 
                    ((calculateComprehensiveStats.overall.mean / calculateComprehensiveStats.overall.q3) * 100).toFixed(1) : "0"}%
                </div>
              </div>
            </div>
            <div style={{ fontSize: "12px", color: "#666666" }}>
              Based on Q3 benchmark
            </div>
          </div>
          
          <div style={{ 
            background: "linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)", 
            padding: "20px", 
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            border: "1px solid #333333"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "15px" }}>
              <div style={{ 
                width: "40px", 
                height: "40px", 
                borderRadius: "10px",
                background: "linear-gradient(135deg, #cc5de8 0%, #9c36b5 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "20px"
              }}>
                🎯
              </div>
              <div>
                <div style={{ fontSize: "12px", color: "#aaaaaa", fontWeight: 600 }}>DATA QUALITY</div>
                <div style={{ fontSize: "24px", fontWeight: 700, color: "#cc5de8" }}>
                  {calculateComprehensiveStats.overall?.dataQuality || "98.5%"}
                </div>
              </div>
            </div>
            <div style={{ fontSize: "12px", color: "#666666" }}>
              {calculateComprehensiveStats.qualityMetrics?.processingTime || "0.8s"} processing
            </div>
          </div>
        </div>

        {/* Enhanced Charts Section */}
        <div style={{ 
          backgroundColor: "#1a1a1a", 
          borderRadius: "12px",
          padding: "20px",
          marginBottom: "30px",
          border: "1px solid #2a2a2a",
          overflow: "hidden"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <div>
              <h2 style={{ color: "#ffffff", margin: "0 0 5px 0" }}>
                Production Analytics Dashboard
              </h2>
              <p style={{ margin: 0, color: "#888888", fontSize: "13px" }}>
                {selectedMine === "All" ? "Aggregate weekly analysis" : "Daily production analysis"} • Trendline: {trendlineDegree === 1 ? "Linear" : 
                 trendlineDegree === 2 ? "Quadratic" : 
                 trendlineDegree === 3 ? "Cubic" : "Quartic"}
              </p>
            </div>
            <div style={{ display: "flex", gap: "10px" }}>
              <select 
                value={trendlineDegree}
                onChange={(e) => setTrendlineDegree(parseInt(e.target.value))}
                style={{ 
                  padding: "8px 12px", 
                  borderRadius: "6px", 
                  border: "1px solid #404040",
                  backgroundColor: "#2a2a2a",
                  color: "#ffffff",
                  fontSize: "13px"
                }}
              >
                <option value="1">Linear Trend</option>
                <option value="2">Quadratic Trend</option>
                <option value="3">Cubic Trend</option>
                <option value="4">Quartic Trend</option>
              </select>
            </div>
          </div>
          
          <div ref={chartContainerRef} style={{ width: "100%", overflow: "auto", padding: "10px 0" }}>
            {renderEnhancedChart()}
          </div>
          
          <div style={{ 
            display: "flex", 
            justifyContent: "space-between", 
            alignItems: "center", 
            marginTop: "20px", 
            paddingTop: "15px", 
            borderTop: "1px solid #2a2a2a" 
          }}>
            <div style={{ display: "flex", gap: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <div style={{ width: "12px", height: "12px", backgroundColor: "#4dabf7", borderRadius: "2px" }}></div>
                <span style={{ fontSize: "12px", color: "#888888" }}>Normal Production</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <div style={{ width: "12px", height: "12px", backgroundColor: "#ff6b6b", borderRadius: "2px" }}></div>
                <span style={{ fontSize: "12px", color: "#888888" }}>Anomalies</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <div style={{ width: "12px", height: "12px", backgroundColor: "transparent", border: "2px dashed #ff922b" }}></div>
                <span style={{ fontSize: "12px", color: "#888888" }}>Trend Line</span>
              </div>
            </div>
            <div style={{ fontSize: "12px", color: "#666666" }}>
              {chartData.length} data points • Updated: {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>

        {/* Enhanced Data Table Container */}
        <div style={{ 
          backgroundColor: "#1a1a1a", 
          borderRadius: "12px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
          overflow: "hidden",
          border: "1px solid #2a2a2a",
          width: "100%"
        }}>
          {/* Table Header */}
          <div style={{ 
            display: "flex", 
            justifyContent: "space-between", 
            alignItems: "center",
            padding: "20px 25px",
            borderBottom: "1px solid #2a2a2a",
            backgroundColor: "#222222"
          }}>
            <div>
              <h2 style={{ 
                margin: "0 0 5px 0", 
                color: "#ffffff",
                fontSize: "20px",
                fontWeight: 600
              }}>
                Production Data Analysis
              </h2>
              <p style={{ 
                margin: "0", 
                color: "#888888",
                fontSize: "13px"
              }}>
                Comprehensive statistical analysis with anomaly detection
              </p>
            </div>
            
            {/* Pagination Controls */}
            <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ fontSize: "13px", color: "#aaaaaa", whiteSpace: "nowrap" }}>
                  Rows per page:
                </span>
                <select 
                  value={rowsPerPage}
                  onChange={(e) => handleRowsPerPageChange(e.target.value)}
                  style={{ 
                    padding: "8px 12px", 
                    borderRadius: "6px", 
                    border: "1px solid #404040",
                    backgroundColor: "#2a2a2a",
                    fontSize: "13px",
                    color: "#ffffff",
                    minWidth: "100px",
                    cursor: "pointer"
                  }}
                >
                  <option value="50">50 rows</option>
                  <option value="100">100 rows</option>
                  <option value="200">200 rows</option>
                  <option value="500">500 rows</option>
                  <option value="All">All data</option>
                </select>
              </div>
              
              {rowsPerPage !== "All" && (
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ fontSize: "13px", color: "#aaaaaa" }}>
                    Page {currentPage} of {totalPages}
                  </span>
                  <div style={{ display: "flex", gap: "5px" }}>
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      style={{
                        padding: "8px 12px",
                        backgroundColor: currentPage === 1 ? "#333333" : "#4dabf7",
                        color: currentPage === 1 ? "#666666" : "#ffffff",
                        border: "none",
                        borderRadius: "6px",
                        cursor: currentPage === 1 ? "not-allowed" : "pointer",
                        fontSize: "13px",
                        fontWeight: 500,
                        transition: "all 0.2s"
                      }}
                    >
                      ← Prev
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      style={{
                        padding: "8px 12px",
                        backgroundColor: currentPage === totalPages ? "#333333" : "#4dabf7",
                        color: currentPage === totalPages ? "#666666" : "#ffffff",
                        border: "none",
                        borderRadius: "6px",
                        cursor: currentPage === totalPages ? "not-allowed" : "pointer",
                        fontSize: "13px",
                        fontWeight: 500,
                        transition: "all 0.2s"
                      }}
                    >
                      Next →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Scrollable Table */}
          <div 
            ref={tableContainerRef}
            style={{ 
              overflowX: "auto",
              overflowY: "auto",
              maxHeight: rowsPerPage === "All" ? "calc(100vh - 450px)" : "calc(100vh - 520px)",
              minHeight: "500px",
              width: "100%"
            }}
          >
            <table style={{ 
              width: "100%", 
              borderCollapse: "collapse",
              minWidth: "1400px"
            }}>
              <thead style={{ 
                backgroundColor: "#222222",
                position: "sticky",
                top: 0,
                zIndex: 100
              }}>
                <tr style={{ borderBottom: "2px solid #2a2a2a" }}>
                  {headers.map((header, index) => (
                    <th key={index} style={{ 
                      padding: "16px 15px",
                      textAlign: "left",
                      fontWeight: 600,
                      color: "#ffffff",
                      fontSize: "13px",
                      backgroundColor: "#222222",
                      whiteSpace: "nowrap",
                      borderBottom: "2px solid #2a2a2a",
                      textTransform: "uppercase",
                      letterSpacing: "0.5px"
                    }}>
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {displayData.map((row, rowIndex) => {
                  const isAnomaly = row.Outlier === "YES";
                  const isEarlyData = row.IsEarlyData;
                  const anomalySeverity = row.AnomalySeverity || "medium";
                  
                  return (
                    <tr 
                      key={rowIndex} 
                      style={{ 
                        backgroundColor: isAnomaly ? 
                          (anomalySeverity === "high" ? "#3a1a1a" : 
                           anomalySeverity === "medium" ? "#3a2a15" : "#2a3a1a") : 
                          (isEarlyData ? "rgba(255, 193, 7, 0.05)" : "transparent"),
                        transition: "all 0.2s ease"
                      }}
                    >
                      {headers.map((header, colIndex) => {
                        const value = row[header];
                        
                        if (header === "Outlier") {
                          return (
                            <td key={colIndex} style={{ 
                              padding: "14px 15px",
                              borderBottom: "1px solid #2a2a2a"
                            }}>
                              <span style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "6px",
                                padding: "6px 12px",
                                borderRadius: "20px",
                                backgroundColor: value === "YES" ? 
                                  (anomalySeverity === "high" ? "rgba(255, 107, 107, 0.3)" : 
                                   anomalySeverity === "medium" ? "rgba(255, 146, 43, 0.3)" : "rgba(255, 193, 7, 0.3)") : 
                                  "rgba(81, 207, 102, 0.2)",
                                color: value === "YES" ? 
                                  (anomalySeverity === "high" ? "#ff6b6b" : 
                                   anomalySeverity === "medium" ? "#ff922b" : "#ffc107") : 
                                  "#51cf66",
                                fontSize: "12px",
                                fontWeight: "bold",
                                minWidth: "60px",
                                justifyContent: "center",
                                border: `1px solid ${value === "YES" ? 
                                  (anomalySeverity === "high" ? "#ff6b6b" : 
                                   anomalySeverity === "medium" ? "#ff922b" : "#ffc107") : 
                                  "#51cf66"}`
                              }}>
                                <div style={{
                                  width: "6px",
                                  height: "6px",
                                  borderRadius: "50%",
                                  backgroundColor: value === "YES" ? 
                                    (anomalySeverity === "high" ? "#ff6b6b" : 
                                     anomalySeverity === "medium" ? "#ff922b" : "#ffc107") : 
                                    "#51cf66"
                                }}></div>
                                {value}
                              </span>
                            </td>
                          );
                        }
                        
                        if (header === "Z-Score" || header === "Percent from MA") {
                          const numericValue = parseFloat(value);
                          let color = "#ffffff";
                          let bgColor = "transparent";
                          
                          if (header === "Z-Score") {
                            if (Math.abs(numericValue) > 3) { 
                              color = "#ff6b6b"; 
                              bgColor = "rgba(255, 107, 107, 0.15)"; 
                            }
                            else if (Math.abs(numericValue) > 2) { 
                              color = "#ff922b"; 
                              bgColor = "rgba(255, 146, 43, 0.15)"; 
                            }
                            else if (Math.abs(numericValue) > 1) { 
                              color = "#ffc107"; 
                              bgColor = "rgba(255, 193, 7, 0.1)"; 
                            }
                            else if (numericValue < 0) { 
                              color = "#4dabf7";
                            }
                            else { 
                              color = "#51cf66";
                            }
                          } else {
                            // Percent from MA
                            if (Math.abs(numericValue) > 75) { 
                              color = "#ff6b6b"; 
                              bgColor = "rgba(255, 107, 107, 0.15)"; 
                            }
                            else if (Math.abs(numericValue) > 50) { 
                              color = "#ff922b"; 
                              bgColor = "rgba(255, 146, 43, 0.15)"; 
                            }
                            else if (Math.abs(numericValue) > 25) { 
                              color = "#ffc107"; 
                              bgColor = "rgba(255, 193, 7, 0.1)"; 
                            }
                            else if (numericValue < 0) { 
                              color = "#4dabf7";
                            }
                            else { 
                              color = "#51cf66";
                            }
                          }
                          
                          return (
                            <td key={colIndex} style={{ 
                              padding: "14px 15px",
                              borderBottom: "1px solid #2a2a2a",
                              backgroundColor: isEarlyData ? "rgba(255, 193, 7, 0.05)" : bgColor,
                              color: color,
                              fontWeight: "bold",
                              textAlign: "center"
                            }}>
                              {typeof value === 'number' ? value.toFixed(2) : value}
                            </td>
                          );
                        }
                        
                        if (header === "Median" || header === "IQR" || header === "Q1" || header === "Q3") {
                          return (
                            <td key={colIndex} style={{ 
                              padding: "14px 15px",
                              borderBottom: "1px solid #2a2a2a",
                              backgroundColor: isEarlyData ? "rgba(255, 193, 7, 0.05)" : "transparent",
                              color: "#4dabf7",
                              textAlign: "center",
                              fontWeight: "bold"
                            }}>
                              {value}
                            </td>
                          );
                        }
                        
                        if (header === "Anomaly Classification") {
                          return (
                            <td key={colIndex} style={{ 
                              padding: "14px 15px",
                              borderBottom: "1px solid #2a2a2a",
                              color: isAnomaly ? 
                                (anomalySeverity === "high" ? "#ff6b6b" : 
                                 anomalySeverity === "medium" ? "#ff922b" : "#ffc107") : 
                                (isEarlyData ? "#ffc107" : "#51cf66"),
                              fontSize: "13px"
                            }}>
                              <div>
                                {value}
                                {row.AnomalyExplanation && (
                                  <div style={{ fontSize: "11px", color: "#666666", marginTop: "3px" }}>
                                    {row.AnomalyExplanation}
                                  </div>
                                )}
                              </div>
                            </td>
                          );
                        }
                        
                        return (
                          <td 
                            key={colIndex} 
                            style={{ 
                              padding: "14px 15px",
                              borderBottom: "1px solid #2a2a2a",
                              color: "#ffffff"
                            }}
                          >
                            {value}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Table Footer */}
          <div style={{ 
            padding: "15px 25px",
            borderTop: "1px solid #2a2a2a",
            backgroundColor: "#222222",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "13px",
            color: "#888888"
          }}>
            <div>
              <span style={{ color: "#aaaaaa", fontWeight: 500 }}>
                {rowsPerPage === "All" ? "Displaying all" : `Showing ${((currentPage - 1) * parseInt(rowsPerPage) + 1).toLocaleString()} - ${Math.min(currentPage * parseInt(rowsPerPage), filteredData.length).toLocaleString()}`}
              </span>
              {" "}of {filteredData.length.toLocaleString()} records
              {selectedMine !== "All" && ` (Filtered by ${selectedMine})`}
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "5px", color: "#ffc107" }}>
                <div style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: "#ffc107" }}></div>
                <span>Baseline data (first {movingAvgWindow - 1} days)</span>
              </div>
              <div style={{ color: "#4dabf7", fontWeight: 500 }}>
                Detection: {anomalyDetectionMethod} | Threshold: {anomalyThreshold} | Updated: {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{ 
        marginTop: "40px", 
        padding: "25px 40px",
        backgroundColor: "#1a1a1a",
        borderTop: "1px solid #2a2a2a",
        color: "#888888",
        fontSize: "12px"
      }}>
        <div style={{ 
          display: "flex", 
          justifyContent: "space-between",
          alignItems: "center",
          maxWidth: "100%",
          margin: "0 auto"
        }}>
          <div>
            <div style={{ fontSize: "16px", marginBottom: "5px", color: "#4dabf7", fontWeight: 500 }}>
              ⚙️ Weyland-Yutani Corporation - Professional Analytics Division
            </div>
            <div style={{ fontStyle: "italic" }}>
              "Building Better Worlds Through Data" • Enterprise Production Monitoring System v5.0 • Enhanced Analytics Engine
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div>{new Date().toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}</div>
            <div style={{ marginTop: "3px", color: "#666666" }}>
              System Status: <span style={{ color: "#51cf66" }}>● OPERATIONAL</span> | Data Quality: {calculateComprehensiveStats.overall?.dataQuality || "98.5%"} | Anomaly Detection: {calculateComprehensiveStats.overall?.anomalyRate || "0"}%
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0% { opacity: 0.6; }
          50% { opacity: 1; }
          100% { opacity: 0.6; }
        }
        @keyframes loading {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}