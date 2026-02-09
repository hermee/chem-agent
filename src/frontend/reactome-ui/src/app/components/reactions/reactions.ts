import { Component, OnInit, signal } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import { AllCommunityModule, ModuleRegistry, ColDef, themeQuartz } from 'ag-grid-community';
import { ApiService, Reaction } from '../../services/api';

ModuleRegistry.registerModules([AllCommunityModule]);

const reactomeTheme = themeQuartz.withParams({
  accentColor: '#10b981',
  backgroundColor: '#ffffff',
  borderColor: '#e2e8f0',
  headerBackgroundColor: '#f8fafc',
  headerTextColor: '#1e293b',
  oddRowBackgroundColor: '#f8fafc',
  rowHoverColor: '#ecfdf5',
  selectedRowBackgroundColor: '#d1fae5',
  fontSize: 13,
  headerFontSize: 13,
  headerHeight: 48,
  spacing: 6,
});

@Component({
  selector: 'app-reactions',
  standalone: true,
  imports: [AgGridAngular],
  templateUrl: './reactions.html',
  styleUrl: './reactions.css',
})
export class Reactions implements OnInit {
  theme = reactomeTheme;
  reactions = signal<Reaction[]>([]);

  colDefs: ColDef[] = [
    { field: 'id', headerName: 'ID', width: 90, filter: 'agNumberColumnFilter' },
    { field: 'name', headerName: 'Reaction', width: 220, filter: 'agTextColumnFilter' },
    { field: 'reactants', headerName: 'Reactants', width: 200, filter: 'agTextColumnFilter' },
    {
      field: 'smarts_reactants', headerName: 'SMARTS (Reactants)', flex: 1,
      cellStyle: { fontFamily: 'monospace', fontSize: '12px' },
    },
    {
      field: 'smarts_product', headerName: 'SMARTS (Product)', flex: 1,
      cellStyle: { fontFamily: 'monospace', fontSize: '12px' },
    },
    {
      field: 'warning', headerName: 'Status', width: 180,
      cellRenderer: (params: any) =>
        params.value
          ? `<span style="background:#fef2f2;color:#dc2626;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:500;">⚠️ ${params.value}</span>`
          : `<span style="background:#ecfdf5;color:#059669;padding:2px 10px;border-radius:6px;font-size:12px;font-weight:500;">✅ Valid</span>`,
    },
  ];

  defaultColDef: ColDef = { sortable: true, filter: true, resizable: true };

  constructor(private api: ApiService) {}

  getSvgUrl(id: number): string {
    return this.api.getReactionSvgUrl(id);
  }

  ngOnInit() {
    this.api.getReactions().subscribe((res) => this.reactions.set(res.reactions));
  }
}
