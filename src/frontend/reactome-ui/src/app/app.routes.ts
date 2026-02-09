import { Routes } from '@angular/router';
import { Chat } from './components/chat/chat';
import { Reactions } from './components/reactions/reactions';
import { Workflow } from './components/workflow/workflow';
import { LnpAgent } from './components/lnp-agent/lnp-agent';

export const routes: Routes = [
  { path: '', component: Chat },
  { path: 'reactions', component: Reactions },
  { path: 'lnp-agent', component: LnpAgent },
  { path: 'workflow', component: Workflow },
];
