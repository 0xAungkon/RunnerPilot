import type { FC } from "react";
import { Outlet } from "react-router-dom";

interface CanvasLayoutProps {
  className?: string;
}

const CanvasLayout: FC<CanvasLayoutProps> = ({ className = "" }) => {
  return (
    <div className={`canvas-layout ${className}`}>
      <Outlet />
    </div>
  );
};

export default CanvasLayout;
