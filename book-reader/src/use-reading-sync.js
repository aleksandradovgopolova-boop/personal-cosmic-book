import { useCallback, useEffect, useRef, useState } from 'react';
import {
  isSupabaseConfigured,
  supabase,
} from './supabase-client.js';

const BOOK_ID = 'bolshe-ne-budu-menshe';
const SYNC_DELAY_MS = 800;

function normalizePage(page) {
  if (!Number.isFinite(page)) return 2;
  return Math.min(40, Math.max(1, Math.round(page)));
}

async function fetchCloudProgress(userId) {
  const { data, error } = await supabase
    .from('reading_progress')
    .select('page_number, updated_at')
    .eq('user_id', userId)
    .eq('book_id', BOOK_ID)
    .maybeSingle();

  if (error) throw error;
  return data;
}

async function fetchCloudEntitlement(userId) {
  const { data, error } = await supabase
    .from('book_entitlements')
    .select('status')
    .eq('user_id', userId)
    .eq('book_id', BOOK_ID)
    .maybeSingle();

  if (error) throw error;
  return data?.status === 'active';
}

async function saveCloudProgress(userId, page, updatedAt) {
  const { error } = await supabase
    .from('reading_progress')
    .upsert(
      {
        user_id: userId,
        book_id: BOOK_ID,
        page_number: normalizePage(page),
        updated_at: new Date(updatedAt).toISOString(),
      },
      { onConflict: 'user_id,book_id' },
    );

  if (error) throw error;
}

export function useReadingSync({
  page,
  updatedAt,
  onRemoteProgress,
  onCloudEntitlement,
}) {
  const [user, setUser] = useState(null);
  const [syncStatus, setSyncStatus] = useState(
    isSupabaseConfigured ? 'loading' : 'local',
  );
  const [syncError, setSyncError] = useState('');
  const latestProgressRef = useRef({ page, updatedAt });
  const cloudReadyRef = useRef(false);

  useEffect(() => {
    latestProgressRef.current = { page, updatedAt };
  }, [page, updatedAt]);

  useEffect(() => {
    if (!supabase) return undefined;

    let active = true;

    supabase.auth.getSession().then(({ data, error }) => {
      if (!active) return;
      if (error) {
        setSyncError(error.message);
        setSyncStatus('error');
        return;
      }
      setUser(data.session?.user || null);
      if (!data.session?.user) setSyncStatus('local');
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!active) return;
      setUser(session?.user || null);
    });

    return () => {
      active = false;
      subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (!supabase || !user) {
      cloudReadyRef.current = false;
      if (isSupabaseConfigured) setSyncStatus('local');
      return undefined;
    }

    let active = true;
    cloudReadyRef.current = false;
    setSyncStatus('loading');
    setSyncError('');

    const mergeProgress = async () => {
      try {
        const [cloudProgress, hasEntitlement] = await Promise.all([
          fetchCloudProgress(user.id),
          fetchCloudEntitlement(user.id),
        ]);

        if (!active) return;

        if (hasEntitlement) onCloudEntitlement();

        const localProgress = latestProgressRef.current;
        const cloudUpdatedAt = cloudProgress?.updated_at
          ? Date.parse(cloudProgress.updated_at)
          : 0;

        if (cloudProgress && cloudUpdatedAt > localProgress.updatedAt) {
          onRemoteProgress(
            normalizePage(cloudProgress.page_number),
            cloudUpdatedAt,
          );
        } else {
          await saveCloudProgress(
            user.id,
            localProgress.page,
            localProgress.updatedAt || Date.now(),
          );
        }

        if (!active) return;
        cloudReadyRef.current = true;
        setSyncStatus('synced');
      } catch (error) {
        if (!active) return;
        setSyncError(error.message || 'Не удалось синхронизировать прогресс.');
        setSyncStatus('error');
      }
    };

    mergeProgress();

    return () => {
      active = false;
      cloudReadyRef.current = false;
    };
  }, [user?.id, onCloudEntitlement, onRemoteProgress]);

  useEffect(() => {
    if (!supabase || !user || !cloudReadyRef.current) return undefined;

    setSyncStatus('saving');
    const timer = window.setTimeout(async () => {
      try {
        await saveCloudProgress(user.id, page, updatedAt || Date.now());
        setSyncError('');
        setSyncStatus('synced');
      } catch (error) {
        setSyncError(error.message || 'Не удалось сохранить прогресс.');
        setSyncStatus('error');
      }
    }, SYNC_DELAY_MS);

    return () => window.clearTimeout(timer);
  }, [page, updatedAt, user?.id]);

  const sendMagicLink = useCallback(async (email) => {
    if (!supabase) {
      throw new Error('Supabase пока не подключён.');
    }

    const redirectTo = `${window.location.origin}${window.location.pathname}`;
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: {
        emailRedirectTo: redirectTo,
        shouldCreateUser: true,
      },
    });

    if (error) throw error;
  }, []);

  const signOut = useCallback(async () => {
    if (!supabase) return;
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    cloudReadyRef.current = false;
    setUser(null);
    setSyncStatus('local');
  }, []);

  return {
    configured: isSupabaseConfigured,
    user,
    syncStatus,
    syncError,
    sendMagicLink,
    signOut,
  };
}
