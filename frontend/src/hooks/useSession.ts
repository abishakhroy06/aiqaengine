import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sessionService } from '../services/sessionService';
import { CreateSessionRequest } from '../types/session';

export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: sessionService.getSessions,
  });
}

export function useSession(id: number) {
  return useQuery({
    queryKey: ['sessions', id],
    queryFn: () => sessionService.getSession(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'generating' || status === 'pending' ? 2000 : false;
    },
  });
}

export function useCreateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (req: CreateSessionRequest) => sessionService.createSession(req),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sessions'] }),
  });
}

export function useDeleteSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => sessionService.deleteSession(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sessions'] }),
  });
}

export function useRegenerateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => sessionService.regenerateSession(id),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['sessions', data.id] });
      qc.invalidateQueries({ queryKey: ['sessions'] });
    },
  });
}
