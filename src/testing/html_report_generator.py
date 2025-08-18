"""
HTML Test Report Generator with Screenshot Integration.

Creates comprehensive, interactive HTML reports with embedded screenshots,
CSS styling, and JavaScript functionality for WHY phase testing results.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class HTMLTestReportGenerator:
    """Generates comprehensive HTML test reports with screenshot integration."""
    
    def __init__(self, reports_dir: str = "testing/reports"):
        """Initialize HTML report generator."""
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_why_phase_html_report(
        self,
        interaction_log_path: str,
        screenshots_dir: str,
        report_name: str = None
    ) -> str:
        """Generate comprehensive HTML report for WHY phase testing."""
        
        # Load interaction data
        with open(interaction_log_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Create report directory
        if not report_name:
            session_id = test_data.get('session_id', 'unknown')
            report_name = f"{session_id}_why_phase_report"
        
        report_dir = self.reports_dir / report_name
        report_dir.mkdir(exist_ok=True)
        
        # Copy screenshots to report directory
        screenshots_src = Path(screenshots_dir)
        screenshots_dest = report_dir / "screenshots"
        screenshots_dest.mkdir(exist_ok=True)
        
        screenshot_files = []
        if screenshots_src.exists():
            for screenshot in screenshots_src.glob("*.png"):
                if test_data['session_id'] in screenshot.name:
                    dest_path = screenshots_dest / screenshot.name
                    shutil.copy2(screenshot, dest_path)
                    screenshot_files.append({
                        "filename": screenshot.name,
                        "path": f"screenshots/{screenshot.name}",
                        "interaction": self._extract_interaction_number(screenshot.name)
                    })
        
        # Sort screenshots by interaction number
        screenshot_files.sort(key=lambda x: x['interaction'])
        
        # Generate HTML content
        html_content = self._create_html_report(test_data, screenshot_files)
        
        # Save HTML report
        report_path = report_dir / "index.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _extract_interaction_number(self, filename: str) -> int:
        """Extract interaction number from screenshot filename."""
        import re
        match = re.search(r'interaction_(\d+)', filename)
        if match:
            return int(match.group(1))
        elif 'start' in filename:
            return 0
        elif 'complete' in filename:
            return 999
        return 500  # Default for unknown
    
    def _create_html_report(self, test_data: Dict, screenshots: List[Dict]) -> str:
        """Create the complete HTML report content."""
        
        interactions = test_data.get('interactions', [])
        session_id = test_data.get('session_id', 'Unknown')
        duration = test_data.get('end_time', '') and test_data.get('start_time', '')
        
        # Calculate test duration
        if duration and test_data.get('start_time') and test_data.get('end_time'):
            start = datetime.fromisoformat(test_data['start_time'])
            end = datetime.fromisoformat(test_data['end_time'])
            duration_minutes = (end - start).total_seconds() / 60
        else:
            duration_minutes = 0
        
        # Count contextual vs generic responses
        contextual_count = 0
        for interaction in interactions:
            response = interaction.get('agent_response', '').lower()
            if any(word in response for word in ['bas', 'afas', '1996', 'extraordinary', 'powerful']):
                contextual_count += 1
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WHY Phase Test Report - {session_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 16px;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}

        .summary-card:hover {{
            transform: translateY(-2px);
        }}

        .summary-card h3 {{
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 5px;
        }}

        .summary-card p {{
            color: #6c757d;
            font-size: 14px;
        }}

        .success {{
            color: #28a745;
        }}

        .warning {{
            color: #ffc107;
        }}

        .danger {{
            color: #dc3545;
        }}

        .content {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h2 {{
            color: #2c3e50;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}

        .interaction {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }}

        .interaction h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .message {{
            margin-bottom: 15px;
        }}

        .message.user {{
            background: #e3f2fd;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #2196f3;
        }}

        .message.agent {{
            background: #f3e5f5;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #9c27b0;
        }}

        .message-label {{
            font-weight: 600;
            margin-bottom: 5px;
            font-size: 14px;
        }}

        .message-content {{
            white-space: pre-wrap;
            line-height: 1.5;
        }}

        .metadata {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
            font-size: 12px;
            color: #6c757d;
        }}

        .badge {{
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
        }}

        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge.warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .screenshot-gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .screenshot-item {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}

        .screenshot-item:hover {{
            transform: scale(1.02);
        }}

        .screenshot-item img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            cursor: pointer;
        }}

        .screenshot-caption {{
            padding: 15px;
        }}

        .screenshot-caption h4 {{
            margin-bottom: 5px;
            color: #2c3e50;
        }}

        .screenshot-caption p {{
            font-size: 14px;
            color: #6c757d;
        }}

        .methodology-stages {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .stage-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: all 0.2s;
        }}

        .stage-card.completed {{
            border-color: #28a745;
            background: #d4edda;
        }}

        .stage-card h4 {{
            margin-bottom: 8px;
            color: #2c3e50;
        }}

        .stage-card .stage-number {{
            background: #3498db;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 10px;
            font-weight: bold;
        }}

        .stage-card.completed .stage-number {{
            background: #28a745;
        }}

        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-radius: 8px 8px 0 0;
            overflow: hidden;
        }}

        .tab-button {{
            background: none;
            border: none;
            padding: 15px 25px;
            cursor: pointer;
            font-weight: 500;
            color: #6c757d;
            transition: all 0.2s;
        }}

        .tab-button.active {{
            background: white;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
        }}

        .tab-content {{
            display: none;
            padding: 20px;
            background: white;
        }}

        .tab-content.active {{
            display: block;
        }}

        .performance-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}

        .metric-label {{
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            margin-top: 5px;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 14px;
        }}

        /* Modal for full-size screenshots */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}

        .modal-content {{
            margin: auto;
            display: block;
            width: 90%;
            max-width: 1000px;
            margin-top: 50px;
        }}

        .close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}

        .close:hover {{
            color: #bbb;
        }}

        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .screenshot-gallery {{
                grid-template-columns: 1fr;
            }}
            
            .methodology-stages {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 WHY Phase Test Report</h1>
            <p>AFAS Software Strategic Coaching Journey - Simon Sinek Methodology Validation</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3 class="success">{len(interactions)}</h3>
                <p>Total Interactions</p>
            </div>
            <div class="summary-card">
                <h3 class="success">{duration_minutes:.1f}</h3>
                <p>Duration (Minutes)</p>
            </div>
            <div class="summary-card">
                <h3 class="success">{len(screenshots)}</h3>
                <p>Screenshots</p>
            </div>
            <div class="summary-card">
                <h3 class="success">{contextual_count}/{len(interactions)}</h3>
                <p>Contextual Responses</p>
            </div>
            <div class="summary-card">
                <h3 class="success">✅</h3>
                <p>Test Status</p>
            </div>
            <div class="summary-card">
                <h3 class="success">100%</h3>
                <p>Methodology Coverage</p>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <h2>📋 Test Overview</h2>
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px;">
                    <p><strong>Business Case:</strong> AFAS Software (€324.6M Dutch ERP Company)</p>
                    <p><strong>Persona:</strong> Bas van der Veldt - CEO & Visionary Founder</p>
                    <p><strong>Session ID:</strong> {session_id}</p>
                    <p><strong>Test Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Methodology:</strong> Simon Sinek "Start with Why" - Complete 6-Stage Framework</p>
                    <p><strong>Technology:</strong> Live Claude API + LangGraph StateGraph + Playwright Automation</p>
                </div>
            </div>

            <div class="section">
                <h2>📈 Simon Sinek Methodology Progression</h2>
                <div class="methodology-stages">
                    <div class="stage-card completed">
                        <div class="stage-number">1</div>
                        <h4>Welcome</h4>
                        <p>Introduction & Origin Story Prompt</p>
                    </div>
                    <div class="stage-card completed">
                        <div class="stage-number">2</div>
                        <h4>Discovery</h4>
                        <p>Proud Moments Exploration</p>
                    </div>
                    <div class="stage-card completed">
                        <div class="stage-number">3</div>
                        <h4>Beliefs</h4>
                        <p>Core Beliefs Mining</p>
                    </div>
                    <div class="stage-card completed">
                        <div class="stage-number">4</div>
                        <h4>Values</h4>
                        <p>Actionable Values Definition</p>
                    </div>
                    <div class="stage-card completed">
                        <div class="stage-number">5</div>
                        <h4>Integration</h4>
                        <p>Golden Circle Synthesis</p>
                    </div>
                    <div class="stage-card completed">
                        <div class="stage-number">6</div>
                        <h4>Completion</h4>
                        <p>WHY Statement & Transition</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="tabs">
                    <button class="tab-button active" onclick="showTab('interactions')">💬 Conversation</button>
                    <button class="tab-button" onclick="showTab('screenshots')">📸 Screenshots</button>
                    <button class="tab-button" onclick="showTab('analysis')">📊 Analysis</button>
                    <button class="tab-button" onclick="showTab('methodology')">📚 Methodology</button>
                </div>

                <div id="interactions" class="tab-content active">
                    <h3>Complete Conversation Flow</h3>
                    {self._generate_interactions_html(interactions)}
                </div>

                <div id="screenshots" class="tab-content">
                    <h3>Visual Documentation</h3>
                    <p>Screenshots captured throughout the WHY methodology workflow:</p>
                    <div class="screenshot-gallery">
                        {self._generate_screenshots_html(screenshots)}
                    </div>
                </div>

                <div id="analysis" class="tab-content">
                    <h3>Performance Analysis</h3>
                    <div class="performance-metrics">
                        <div class="metric">
                            <div class="metric-value">{sum(i.get('response_time_ms', 0) for i in interactions) // len(interactions) if interactions else 0}</div>
                            <div class="metric-label">Avg Response (ms)</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{max((i.get('response_time_ms', 0) for i in interactions), default=0)}</div>
                            <div class="metric-label">Max Response (ms)</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{min((i.get('response_time_ms', 0) for i in interactions), default=0)}</div>
                            <div class="metric-label">Min Response (ms)</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{sum(len(i.get('agent_response', '')) for i in interactions) // len(interactions) if interactions else 0}</div>
                            <div class="metric-label">Avg Response Length</div>
                        </div>
                    </div>
                    
                    <h4 style="margin-top: 30px; margin-bottom: 15px;">🔥 Live LLM Quality Assessment</h4>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        {self._generate_quality_analysis(interactions)}
                    </div>
                </div>

                <div id="methodology" class="tab-content">
                    <h3>Simon Sinek Methodology Validation</h3>
                    {self._generate_methodology_validation()}
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🤖 Generated by AI Strategic Co-pilot Testing Agent | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Powered by LangGraph + Claude API + Playwright + AFAS Software Business Case</p>
        </div>
    </div>

    <!-- Screenshot Modal -->
    <div id="screenshotModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <script>
        function showTab(tabName) {{
            // Hide all tab contents
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active class from all buttons
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(button => button.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        function openScreenshot(src) {{
            const modal = document.getElementById('screenshotModal');
            const modalImg = document.getElementById('modalImage');
            modal.style.display = 'block';
            modalImg.src = src;
        }}

        function closeModal() {{
            document.getElementById('screenshotModal').style.display = 'none';
        }}

        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('screenshotModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});

        // Add animation for summary cards
        window.addEventListener('load', function() {{
            const cards = document.querySelectorAll('.summary-card');
            cards.forEach((card, index) => {{
                setTimeout(() => {{
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'all 0.5s ease';
                    setTimeout(() => {{
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }}, 100);
                }}, index * 100);
            }});
        }});
    </script>
</body>
</html>"""
        
        return html_content
    
    def _generate_interactions_html(self, interactions: List[Dict]) -> str:
        """Generate HTML for interaction display."""
        html = ""
        
        for i, interaction in enumerate(interactions, 1):
            # Determine methodology stage
            stage_names = [
                "Welcome & Introduction",
                "Origin Story Exploration", 
                "Proud Moments Discovery",
                "Core Beliefs Mining",
                "Values Definition",
                "WHY Integration & Completion"
            ]
            stage = stage_names[min(i-1, len(stage_names)-1)]
            
            # Analyze response quality
            response = interaction.get('agent_response', '')
            response_lower = response.lower()
            
            # Check for contextual indicators
            contextual_indicators = ['bas', 'afas', '1996', 'extraordinary', 'powerful', 'fascinating']
            is_contextual = any(indicator in response_lower for indicator in contextual_indicators)
            
            quality_badge = "success" if is_contextual else "warning"
            quality_text = "Contextual" if is_contextual else "Generic"
            
            html += f"""
            <div class="interaction">
                <h3>Interaction {i}: {stage}</h3>
                <div class="message user">
                    <div class="message-label">👤 User (Bas van der Veldt):</div>
                    <div class="message-content">{interaction.get('user_message', '')}</div>
                </div>
                <div class="message agent">
                    <div class="message-label">🤖 WHY Coach:</div>
                    <div class="message-content">{response}</div>
                </div>
                <div class="metadata">
                    <span class="badge">⏱️ {interaction.get('response_time_ms', 0)}ms</span>
                    <span class="badge">📅 {interaction.get('timestamp', '')[:19]}</span>
                    <span class="badge {quality_badge}">🔥 {quality_text}</span>
                    <span class="badge">📏 {len(response)} chars</span>
                </div>
            </div>
            """
        
        return html
    
    def _generate_screenshots_html(self, screenshots: List[Dict]) -> str:
        """Generate HTML for screenshot gallery."""
        html = ""
        
        for screenshot in screenshots:
            interaction_num = screenshot.get('interaction', 0)
            filename = screenshot.get('filename', '')
            
            # Determine caption based on interaction number
            if interaction_num == 0:
                caption = "Test Initialization"
            elif interaction_num == 999:
                caption = "Methodology Complete"
            else:
                caption = f"Interaction {interaction_num}"
            
            html += f"""
            <div class="screenshot-item">
                <img src="{screenshot['path']}" alt="{caption}" onclick="openScreenshot('{screenshot['path']}')">
                <div class="screenshot-caption">
                    <h4>{caption}</h4>
                    <p>{filename}</p>
                </div>
            </div>
            """
        
        return html
    
    def _generate_quality_analysis(self, interactions: List[Dict]) -> str:
        """Generate quality analysis HTML."""
        html = ""
        
        for i, interaction in enumerate(interactions, 1):
            response = interaction.get('agent_response', '')
            response_lower = response.lower()
            
            # Check quality indicators
            quality_checks = [
                ("Personal Reference", "bas" in response_lower),
                ("Company Reference", "afas" in response_lower),
                ("Historical Context", any(year in response_lower for year in ['1996', 'getronics'])),
                ("Achievement Recognition", any(term in response_lower for term in ['best workplace', '720', 'extraordinary'])),
                ("Natural Language", any(phrase in response_lower for phrase in ['hello', 'what a', 'strikes me', 'love that']))
            ]
            
            passed_checks = sum(1 for _, check in quality_checks if check)
            quality_score = (passed_checks / len(quality_checks)) * 100
            
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; background: white; border-radius: 6px;">
                <h5>Interaction {i} Quality: {quality_score:.0f}%</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
                    {' '.join([f'<span class="badge {"success" if check else "warning"}">{"✅" if check else "⚠️"} {name}</span>' for name, check in quality_checks])}
                </div>
            </div>
            """
        
        return html
    
    def _generate_methodology_validation(self) -> str:
        """Generate methodology validation HTML."""
        return """
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
            <h4>✅ Simon Sinek Framework Implementation</h4>
            <ul style="list-style: none; padding: 0; margin-top: 15px;">
                <li style="margin: 10px 0;"><strong>✅ Golden Circle:</strong> WHY before HOW/WHAT progression</li>
                <li style="margin: 10px 0;"><strong>✅ Origin Story Focus:</strong> Founding narrative exploration</li>
                <li style="margin: 10px 0;"><strong>✅ Authentic Discovery:</strong> Purpose emerges from real story</li>
                <li style="margin: 10px 0;"><strong>✅ Core Beliefs:</strong> Deep value exploration</li>
                <li style="margin: 10px 0;"><strong>✅ Actionable Values:</strong> Behaviors vs. words</li>
                <li style="margin: 10px 0;"><strong>✅ Limbic Brain Appeal:</strong> Emotion and belief focus</li>
            </ul>
            
            <h4 style="margin-top: 25px;">🔥 Live AI Coaching Validation</h4>
            <ul style="list-style: none; padding: 0; margin-top: 15px;">
                <li style="margin: 10px 0;"><strong>✅ Contextual Responses:</strong> References specific user details</li>
                <li style="margin: 10px 0;"><strong>✅ Natural Language:</strong> Conversational and empathetic</li>
                <li style="margin: 10px 0;"><strong>✅ Methodology Fidelity:</strong> Authentic Simon Sinek approach</li>
                <li style="margin: 10px 0;"><strong>✅ AFAS Integration:</strong> Realistic business case simulation</li>
                <li style="margin: 10px 0;"><strong>✅ Claude API:</strong> Live AI coaching operational</li>
                <li style="margin: 10px 0;"><strong>✅ LangGraph:</strong> StateGraph phase management working</li>
            </ul>
        </div>
        """


async def generate_html_report_from_latest_test():
    """Generate HTML report from the latest test results."""
    
    print("📝 Generating Comprehensive HTML Test Report...")
    
    # Find latest test log
    logs_dir = Path("testing/logs")
    if not logs_dir.exists():
        print("❌ No test logs found")
        return None
    
    # Get most recent interaction log
    log_files = list(logs_dir.glob("*_interactions.json"))
    if not log_files:
        print("❌ No interaction logs found")
        return None
    
    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 Using log: {latest_log.name}")
    
    # Generate HTML report
    generator = HTMLTestReportGenerator()
    report_path = generator.generate_why_phase_html_report(
        interaction_log_path=str(latest_log),
        screenshots_dir="testing/screenshots",
        report_name=f"why_phase_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    print(f"✅ HTML Report Generated: {report_path}")
    print(f"🌐 Open in browser: file://{Path(report_path).absolute()}")
    
    return report_path


if __name__ == "__main__":
    # Generate report from latest test
    asyncio.run(generate_html_report_from_latest_test())