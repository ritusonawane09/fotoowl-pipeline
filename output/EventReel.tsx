import { Composition, Sequence, AbsoluteFill, Img, useCurrentFrame } from 'remotion';
import React from 'react';

const fps = 30;

const Scene: React.FC<{
  image: string;
  durationInFrames: number;
  caption?: string;
}> = ({ image, durationInFrames, caption }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      <Img
        src={image}
        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
      />
      {caption ? (
        <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 60 }}>
          <div style={{ color: 'white', fontSize: 48, fontFamily: 'sans-serif', textShadow: '0 2px 8px rgba(0,0,0,0.6)' }}>
            {caption}
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

export const EventReel: React.FC = () => {
  const scene1Duration = 4.0 * fps;
  const scene2Duration = 4.0 * fps;
  const scene3Duration = 5.0 * fps;

  const totalDuration = scene1Duration + scene2Duration + scene3Duration;

  return (
    <Composition
      id="EventReel"
      component={EventReel}
      durationInFrames={totalDuration}
      fps={fps}
      width={1920}
      height={1080}
      defaultProps={{}}
    >
      <Sequence from={0} durationInFrames={scene1Duration}>
        <Scene image="input_images/DSC_6588.jpg" durationInFrames={scene1Duration} caption="A radiant bride." />
      </Sequence>
      <Sequence from={scene1Duration} durationInFrames={scene2Duration}>
        <Scene image="input_images/DSC_6596.jpg" durationInFrames={scene2Duration} caption="" />
      </Sequence>
      <Sequence from={scene1Duration + scene2Duration} durationInFrames={scene3Duration}>
        <Scene image="input_images/DSC_6605.jpg" durationInFrames={scene3Duration} caption="Embracing tradition." />
      </Sequence>
    </Composition>
  );
};