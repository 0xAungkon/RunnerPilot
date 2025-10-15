"use client";
import React, { isValidElement } from "react";
import type { ReactElement, ComponentType } from "react";
import { useNavigate } from "react-router-dom";
import { BugIcon } from "lucide-react";

import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

/** Error Page Component */
interface ErrorPageProps {
  smallTitle?: string | ReactElement;
  title?: string | ReactElement;
  description?: string | ReactElement;
  icon?: ReactElement | ComponentType<any>;
}

export const ErrorPage: React.FC<ErrorPageProps> = ({
  smallTitle = "ERROR",
  title = "Something went wrong. Please contact support.",
  description,
  icon = (
    <BugIcon
      className="w-24 h-24 mb-6 "
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    />
  ),
}) => {
  const ICON_PROPS = {
    className: "w-24 h-24 mb-6 ",
    fill: "none",
    stroke: "currentColor",
    viewBox: "0 0 24 24",
  };

  let renderedIcon: ReactElement;
  if (isValidElement(icon)) {
    renderedIcon = icon;
  } else {
    const IconComponent = icon as ComponentType<any>;
    renderedIcon = <IconComponent {...ICON_PROPS} />;
  }

  const navigate = useNavigate();

  return (
   <main className="flex items-center justify-center min-h-screen bg-background text-foreground px-6">
  <Card className="w-full max-w-md">
    <CardHeader className="flex flex-col items-center space-y-4 pb-2">
      {renderedIcon}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold">{smallTitle}</h1>
        <h2 className="text-xl font-medium">{title}</h2>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>
    </CardHeader>

    <CardContent className="pt-4">
      <div className="flex flex-col sm:flex-row gap-3 w-full">
        <Button variant="outline" className="flex-1" onClick={() => navigate(-1)}>
          Go Back
        </Button>
        <Button className="flex-1" onClick={() => navigate("/")}>
          Go Home
        </Button>
      </div>
    </CardContent>

    <CardFooter className="flex justify-center pt-6">
      <a href="mailto:support@example.com" className="text-xs text-muted-foreground">
        Need help? Contact support
      </a>
    </CardFooter>
  </Card>
</main>


  );
};

export default ErrorPage;
