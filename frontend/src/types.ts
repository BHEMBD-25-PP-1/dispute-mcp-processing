export type CaseStatus = 'new' | 'processing' | 'attention' | 'resolved';

export type ConnectorStatus = 'ready' | 'queued' | 'running' | 'done' | 'failed';

export type ServiceKind = 'taxi' | 'afisha' | 'unknown';

export type ParsedIdentifiers = {
  orderId?: string;
  transactionId?: string;
  userId?: string;
  service: ServiceKind;
  confidence: number;
};

export type ConnectorField = {
  label: string;
  value: string;
};

export type McpConnector = {
  id: string;
  name: string;
  service: Exclude<ServiceKind, 'unknown'>;
  status: ConnectorStatus;
  sla: string;
  confidence: number;
  fields: ConnectorField[];
};

export type TimelineEvent = {
  id: string;
  title: string;
  detail: string;
  time: string;
  status: 'info' | 'success' | 'warning';
};

export type DisputeCase = {
  id: string;
  title: string;
  partner: string;
  channel: string;
  priority: 'P1' | 'P2' | 'P3';
  status: CaseStatus;
  receivedAt: string;
  amount: string;
  customerName: string;
  message: string;
  identifiers: ParsedIdentifiers;
  connectors: McpConnector[];
  timeline: TimelineEvent[];
  result: string;
};
