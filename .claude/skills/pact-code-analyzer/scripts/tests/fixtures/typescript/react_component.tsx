/**
 * Test fixture for React TypeScript component (regex fallback testing).
 *
 * Expected Complexity Analysis Results (Regex Fallback):
 * - UserCard: Complexity 3-4 (if, ternary operators in JSX)
 * - formatDate: Complexity 2 (ternary)
 *
 * Expected File Metrics:
 * - Total lines: ~50
 * - Functions: 2
 * - Classes: 0
 * - Imports: 1
 */

import React from 'react';

interface UserCardProps {
  name: string;
  email: string;
  joined?: Date;
  isActive?: boolean;
}

const UserCard: React.FC<UserCardProps> = ({ name, email, joined, isActive = true }) => {
  /**
   * Complexity (estimated): 3-4
   * - Base: 1
   * - ternary (isActive): +1
   * - ternary (joined): +1
   * - if (!name): +1
   */
  if (!name) {
    return null;
  }

  return (
    <div className={`user-card ${isActive ? 'active' : 'inactive'}`}>
      <h2>{name}</h2>
      <p>{email}</p>
      {joined && <p>Joined: {formatDate(joined)}</p>}
    </div>
  );
};

function formatDate(date: Date): string {
  /**
   * Complexity (estimated): 2
   * - Base: 1
   * - ternary: +1
   */
  return date instanceof Date
    ? date.toLocaleDateString()
    : 'Invalid date';
}

export default UserCard;
export { formatDate };
