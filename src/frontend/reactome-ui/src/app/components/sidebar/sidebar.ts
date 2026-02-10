import { Component, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ApiService } from '../../services/api';
import { ConversationService } from '../../services/conversation';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class Sidebar implements OnInit {
  connected = false;
  navItems = [
    { icon: '💬', label: 'Chat', route: '/' },
    { icon: '⚗️', label: 'Reactions', route: '/reactions' },
    { icon: '🤖', label: 'AI-LNP Agent', route: '/lnp-agent' },
    { icon: '🔄', label: 'Workflow', route: '/workflow' },
  ];

  constructor(private api: ApiService, public convService: ConversationService) {}

  ngOnInit() {
    this.api.getHealth().subscribe({
      next: () => (this.connected = true),
      error: () => (this.connected = false),
    });
  }
}
