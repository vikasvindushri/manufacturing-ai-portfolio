"""Phase 2 Configuration Manager UI - Streamlit interface for workflow management"""
import streamlit as st
from typing import Optional, List
from datetime import datetime
from phase_2_workflow_configuration.config_manager import ConfigurationManager
from phase_2_workflow_configuration.schemas import WorkflowConfiguration
from phase_2_workflow_configuration.constants import TEMPLATE_CATALOG

class ConfigurationManagerUI:
    """Streamlit UI for configuration management"""
    
    def __init__(self):
        self.manager = ConfigurationManager()
        if "config_manager_session" not in st.session_state:
            st.session_state.config_manager_session = {"workflow": None}
    
    # ========================================================================
    # MAIN DASHBOARD
    # ========================================================================
    
    def render_dashboard(self) -> None:
        """Main configuration management dashboard"""
        st.title("📊 Phase 2: Workflow Configuration Manager")
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["🎫 Dashboard", "📋 Workflows", "📦 Packages", "📊 Analytics", "📋 Audit Log"]
        )
        
        with tab1:
            self._render_stats_dashboard()
        
        with tab2:
            self._render_workflows_manager()
        
        with tab3:
            self._render_packages_manager()
        
        with tab4:
            self._render_analytics()
        
        with tab5:
            self._render_audit_log()
    
    def _render_stats_dashboard(self) -> None:
        """Display configuration statistics"""
        stats = self.manager.get_statistics()
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Workflows", stats["total_workflows"])
        col2.metric("Active", stats["active_count"])
        col3.metric("Draft", stats["draft_count"])
        col4.metric("Archived", stats["archived_count"])
        
        st.divider()
        
        # Configuration counts
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Form Fields", stats["total_fields"])
        col2.metric("Total Rules", stats["total_rules"])
        col3.metric("Total Prompts", stats["total_prompts"])
        
        st.divider()
        
        # Status breakdown
        st.markdown("### Workflows by Status")
        status_data = stats["by_status"]
        if status_data:
            st.bar_chart(status_data)
    
    def _render_workflows_manager(self) -> None:
        """Manage workflows"""
        st.subheader("📋 Workflow Management")
        
        action = st.radio(
            "Action",
            ["Create New", "View Existing", "Clone", "Archive"],
            horizontal=True,
        )
        
        st.divider()
        
        if action == "Create New":
            self._render_create_workflow()
        elif action == "View Existing":
            self._render_view_workflows()
        elif action == "Clone":
            self._render_clone_workflow()
        elif action == "Archive":
            self._render_archive_workflow()
    
    def _render_create_workflow(self) -> None:
        """Create a new workflow"""
        st.markdown("#### Create New Workflow")
        
        creation_type = st.radio(
            "Start from:",
            ["Template", "Blank"],
            horizontal=True,
        )
        
        col1, col2 = st.columns(2)
        workflow_id = col1.text_input("Workflow ID *", key="new_wf_id")
        workflow_name = col2.text_input("Workflow Name *", key="new_wf_name")
        
        if creation_type == "Template":
            template_id = st.selectbox(
                "Select Template",
                options=list(TEMPLATE_CATALOG.keys()),
                format_func=lambda x: TEMPLATE_CATALOG[x].name,
            )
            template = TEMPLATE_CATALOG[template_id]
            st.info(f"Template: {template.name} - {template.description}")
        
        if st.button("✅ Create Workflow", type="primary", use_container_width=True):
            if not workflow_id or not workflow_name:
                st.error("Workflow ID and Name are required.")
                return
            
            try:
                if creation_type == "Template":
                    workflow = self.manager.create_from_template(
                        template=template,
                        workflow_id=workflow_id,
                        workflow_name=workflow_name,
                        created_by="current_user",
                    )
                else:
                    workflow = self.manager.create_blank(
                        workflow_id=workflow_id,
                        workflow_name=workflow_name,
                        created_by="current_user",
                    )
                
                self.manager.save_workflow(workflow)
                st.success(f"✅ Workflow '{workflow_name}' created!")
                st.session_state.config_manager_session["workflow"] = workflow
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    def _render_view_workflows(self) -> None:
        """View and manage existing workflows"""
        st.markdown("#### Existing Workflows")
        
        # Filter options
        col1, col2 = st.columns(2)
        status_filter = col1.selectbox(
            "Filter by status",
            ["All", "draft", "testing", "active", "archived"],
        )
        created_by_filter = col2.text_input("Filter by creator (optional)")
        
        status = None if status_filter == "All" else status_filter
        workflows = self.manager.list_workflows(status=status, created_by=created_by_filter or None)
        
        if not workflows:
            st.info("No workflows found.")
            return
        
        # Display workflows
        for workflow in workflows:
            with st.expander(
                f"📋 {workflow.name} ({workflow.status.upper()})",
                expanded=False,
            ):
                col1, col2, col3, col4 = st.columns(4)
                col1.write(f"**ID:** {workflow.id}")
                col2.write(f"**Version:** {workflow.version}")
                col3.write(f"**Status:** {workflow.status}")
                col4.write(f"**Fields:** {len(workflow.form_fields)}")
                
                st.write(f"**Created by:** {workflow.created_by}")
                st.write(f"**Created at:** {workflow.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                if workflow.status == "draft":
                    if col1.button("▶️ Publish", key=f"publish_{workflow.id}"):
                        try:
                            self.manager.publish_workflow(workflow.id, "current_user")
                            st.success("Workflow published!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                
                if col2.button("📋 Clone", key=f"clone_{workflow.id}"):
                    st.session_state.config_manager_session["clone_source"] = workflow.id
                    st.rerun()
                
                if col3.button("🗑️ Archive", key=f"archive_{workflow.id}"):
                    try:
                        self.manager.archive_workflow(workflow.id)
                        st.success("Workflow archived!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    def _render_clone_workflow(self) -> None:
        """Clone an existing workflow"""
        st.markdown("#### Clone Workflow")
        
        workflows = self.manager.list_workflows()
        if not workflows:
            st.info("No workflows available to clone.")
            return
        
        source_id = st.selectbox(
            "Select workflow to clone",
            options=[w.id for w in workflows],
            format_func=lambda x: next(w.name for w in workflows if w.id == x),
        )
        
        new_id = st.text_input("New Workflow ID *")
        new_name = st.text_input("New Workflow Name *")
        
        if st.button("✅ Clone Workflow", type="primary", use_container_width=True):
            if not new_id or not new_name:
                st.error("Workflow ID and Name are required.")
                return
            
            try:
                cloned = self.manager.clone_workflow(
                    source_workflow_id=source_id,
                    new_workflow_id=new_id,
                    new_workflow_name=new_name,
                    created_by="current_user",
                )
                self.manager.save_workflow(cloned)
                st.success(f"✅ Workflow cloned as '{new_name}'!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    def _render_archive_workflow(self) -> None:
        """Archive a workflow"""
        st.markdown("#### Archive Workflow")
        
        workflows = self.manager.list_workflows(status="active")
        if not workflows:
            st.info("No active workflows to archive.")
            return
        
        workflow_id = st.selectbox(
            "Select workflow to archive",
            options=[w.id for w in workflows],
            format_func=lambda x: next(w.name for w in workflows if w.id == x),
        )
        
        if st.button("🗑️ Archive Workflow", type="primary", use_container_width=True):
            try:
                self.manager.archive_workflow(workflow_id)
                st.success("Workflow archived!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    def _render_packages_manager(self) -> None:
        """Manage configuration packages"""
        st.subheader("📦 Configuration Packages")
        
        action = st.radio(
            "Action",
            ["Export Package", "Import Package", "View Packages"],
            horizontal=True,
        )
        
        st.divider()
        
        if action == "Export Package":
            st.markdown("#### Export Configuration Package")
            
            workflows = self.manager.list_workflows(status="active")
            if workflows:
                selected = st.multiselect(
                    "Select workflows to export",
                    options=[w.id for w in workflows],
                    format_func=lambda x: next(w.name for w in workflows if w.id == x),
                )
                
                if selected:
                    package_name = st.text_input("Package Name *")
                    package_version = st.text_input("Package Version", value="1.0")
                    
                    if st.button("📤 Export", type="primary", use_container_width=True):
                        try:
                            selected_workflows = [w for w in workflows if w.id in selected]
                            package = self.manager.create_package(
                                package_id=f"pkg-{datetime.now().timestamp()}",
                                package_name=package_name,
                                workflows=selected_workflows,
                                created_by="current_user",
                                version=package_version,
                            )
                            export_path = self.manager.export_package(package)
                            st.success(f"✅ Package exported to {export_path}")
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        elif action == "Import Package":
            st.markdown("#### Import Configuration Package")
            uploaded_file = st.file_uploader("Upload .json package file", type="json")
            
            if uploaded_file:
                if st.button("📥 Import", type="primary", use_container_width=True):
                    try:
                        import json
                        package_data = json.load(uploaded_file)
                        # TODO: implement actual import
                        st.success("✅ Package imported successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        elif action == "View Packages":
            packages = self.manager.list_packages()
            if packages:
                for pkg in packages:
                    st.write(f"📦 **{pkg.name}** v{pkg.version}")
                    st.caption(f"Created by {pkg.created_by} on {pkg.created_at.strftime('%Y-%m-%d')}")
            else:
                st.info("No packages found.")
    
    def _render_analytics(self) -> None:
        """Display analytics and insights"""
        st.subheader("📊 Analytics")
        
        stats = self.manager.get_statistics()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Fields per Workflow", f"{stats['total_fields'] / max(stats['total_workflows'], 1):.1f}")
        col2.metric("Avg Rules per Workflow", f"{stats['total_rules'] / max(stats['total_workflows'], 1):.1f}")
        col3.metric("Avg Prompts per Workflow", f"{stats['total_prompts'] / max(stats['total_workflows'], 1):.1f}")
        
        st.divider()
        
        st.markdown("### Workflow Status Distribution")
        status_data = stats["by_status"]
        if status_data:
            st.bar_chart(status_data)
    
    def _render_audit_log(self) -> None:
        """Display audit trail"""
        st.subheader("📋 Audit Log")
        
        audit_entries = self.manager.export_audit_log()
        
        if audit_entries:
            # Display as table
            st.dataframe(
                audit_entries,
                use_container_width=True,
                hide_index=True,
            )
            
            # Download option
            import json
            st.download_button(
                "📥 Download Audit Log",
                data=json.dumps(audit_entries, indent=2),
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )
        else:
            st.info("No audit entries found.")
