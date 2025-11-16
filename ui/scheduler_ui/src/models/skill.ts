export interface SkillRead {
  id: string;
  name: string;
}

export interface SkillUpdate {
  name: string;
}

export interface SkillCreate {
  name: string;
}

export function newSkillCreate(): SkillCreate {
  return {
    name: '',
  };
}
