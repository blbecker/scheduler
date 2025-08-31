export interface Shift {
  id: string;
  reversed_id: string;
  flerp?: string;
}

export interface Todo {
  id: number;
  content: string;
}

export interface Meta {
  totalCount: number;
}
